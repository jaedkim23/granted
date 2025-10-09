from datetime import datetime
import re
import requests
import pandas as pd
import numpy as np
import difflib
from io import BytesIO
from HERD_functions import *
from sqlalchemy import create_engine, text, bindparam
import sys

### Each year has a different 5-digit identifier
## https://ncses.nsf.gov/surveys/higher-education-research-development/2023#data

tabx_sub1 = "https://ncses.nsf.gov/pubs/nsf"
tabx_sub2 = "/assets/data-tables/tables/nsf"

year_id_lookup = {'2023': 25314, '2022': 24308, '2021': 23304}
year_id = year_id_lookup['2023']

tabs = []

### Table 21: Higher education R&D expenditures, ranked by R&D expenditures
tab21_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab021.xlsx"
tabs.append(tab21_link)

# The link should be of the file directly
url = tabs[0]

# Table 21
r = requests.get(url)
if r.status_code == 200:
    excel_data= BytesIO(r.content)
    df = pd.read_excel(excel_data)
else:
     print(f"Failed to download the file. Status code: {r.status_code}")

comp_row = find_best_header(df.iloc[:21])
head_rows = df.iloc[:(1+comp_row)]

rows_as_lists = [row.dropna().tolist() for _, row in head_rows.iterrows()]

tbl_title = rows_as_lists[0]

for i in range(len(rows_as_lists)):
     row = rows_as_lists[i]
     if any("rank" in str(cell).lower() for cell in row) and any("institution" in str(cell).lower() for cell in row):
        print(row)
        break

top_row = rows_as_lists[i]

start_rec = df.iloc[(i+1):].copy()
col_na_cnt = start_rec.isna().sum(axis=0)
col_names = col_na_cnt[col_na_cnt>=len(start_rec)/2].index.tolist()

start_rec.drop(columns= col_names, inplace=True)
start_rec.columns = top_row

########## Need to find institution names with superscript
# Inst_names = start_rec['Institution']
# Inst_names[Inst_names.str.endswith(tuple(['a','b','c','d','e','f','g']))]

# choose object columns (strings) to convert
obj_cols = start_rec.iloc[:,1:].columns

# Remove everything except digits, dot and minus; 2) replace empty -> NaN; 3) convert
start_rec[obj_cols] = (
    start_rec[obj_cols]
    .astype(str)  # ensure string so replace works
    .replace(r'[^0-9\.\-]', '', regex=True)   # remove commas, $ signs, letters, etc.
    .replace('', np.nan)                      # empty -> NaN
    .apply(pd.to_numeric, errors='coerce')    # convert to numeric, invalid -> NaN
)

# --- Connection Details ---
db_host = "usd-herd-v1.cqdtwkd0m95b.us-west-2.rds.amazonaws.com"
db_port =  3306
db_user = "usd_admin"
db_password =  "USDherdDB"
db_name =  "HERD"

try:
    connection_string = (
        f"mariadb+mariadbconnector://{db_user}:{db_password}@"
        f"{db_host}:{db_port}/{db_name}"
    )
    # Create a dictionary with the SSL arguments
    ssl_args = {'ssl': True}
    # Pass this dictionary to the connect_args parameter
    engine = create_engine(
        connection_string,
        connect_args=ssl_args
    )
    print("SQLAlchemy engine created successfully.")
except Exception as e:
    print(f"Error creating engine: {e}")
    sys.exit(1)

conn = engine.connect()

#### Find relevant schools
inst_names = start_rec['Institution'].unique().tolist()
# Build one named placeholder per item
placeholders = [f":n{i}" for i in range(len(inst_names))]
in_clause = ", ".join(placeholders)
params = {f"n{i}": v for i, v in enumerate(inst_names)}
check_qry = text(f"SELECT inst_id, inst_name FROM institution WHERE inst_name IN ({in_clause})")
inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

# normalize by lower/strip
norm_inst = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_names]
norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_lookup['inst_name']]  

missing_inst = [orig for orig, norm in zip(inst_names, norm_inst) if norm not in set(norm_db)]

### Insert institution records
### UPDATE: need to check institution names
### U. South Floridad vs U. South Floridae

for i in range(len(missing_inst)):
    qry = text("INSERT INTO institution (inst_name, last_update) VALUES (:inst_name, :today_date)")
    record_to_insert = {"inst_name": missing_inst[i], "today_date": datetime.now()}
    conn.execute(qry, record_to_insert)
conn.commit()

inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

#### Insert yearly funding records
all_numeric = all(isinstance(c, (int, float)) for c in start_rec.columns)
years_in_df = [c for c in start_rec.columns if isinstance(c, (int, float))]
years_in_df.insert(0, 'Institution')
df_sub = start_rec.loc[:,years_in_df]

for j in range(1,df_sub.shape[1]):
    yearx = df_sub.columns[j]
    df_year = df_sub[['Institution', yearx]]
    for i in range(len(df_year)):
        inst_x = df_year.iloc[i]['Institution']
        inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x.lower()]['inst_id'].values
        check_qry = text("SELECT 1 FROM herd21 WHERE year = :year AND inst_id = :inst_id_val")
        check_result = conn.execute(check_qry, {"year": yearx, "inst_id_val": int(inst_id_val[0])})

        if not check_result.fetchone():
            qry = text("INSERT INTO herd21 (inst_id, year, value) VALUES (:inst_id_val, :year, :amount)")
            amount = None if pd.isna(float(df_year.iloc[i, 1])) else float(df_year.iloc[i, 1])
            record_to_insert = {"inst_id_val": int(inst_id_val[0]), "year": yearx, "amount": amount}
            conn.execute(qry, record_to_insert)
    conn.commit()

#### Insert yearly funding ranking records
rank_year = max(years_in_df[1:])
rank_year_df = start_rec.loc[:,['Institution','Rank']]
rank_year_df = rank_year_df[~rank_year_df['Rank'].isna()]

for i in range(len(rank_year_df)):
    inst_x = rank_year_df.iloc[i]['Institution']
    inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x.lower()]['inst_id'].values
    check_qry = text("SELECT 1 FROM herd_rank WHERE year = :year AND inst_id = :inst_id_val")
    check_result = conn.execute(check_qry, {"year": rank_year, "inst_id_val": int(inst_id_val[0])})

    if not check_result.fetchone():
        qry = text("INSERT INTO herd_rank (inst_id, year, rank) VALUES (:inst_id_val, :year, :val)")
        rank = None if pd.isna(float(rank_year_df.iloc[i, 1])) else float(rank_year_df.iloc[i, 1])
        record_to_insert = {"inst_id_val": int(inst_id_val[0]), "year": rank_year, "val": rank}
        conn.execute(qry, record_to_insert)
conn.commit()
engine.dispose()


year_id_lookup = {'2023': 25314, '2022': 24308, '2021': 23304}
year_id = year_id_lookup['2021']

tabs = []

### Table 21: Higher education R&D expenditures, ranked by R&D expenditures
tab21_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab021.xlsx"
tabs.append(tab21_link)

### Table 22: Higher education R&D expenditures, ranked by R&D expenditures, by source of funds
tab22_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab022.xlsx"
tabs.append(tab22_link)

# The link should be of the file directly
url = tabs[1]

r = requests.get(url)
if r.status_code == 200:
    excel_data= BytesIO(r.content)
    df = pd.read_excel(excel_data)
else:
     print(f"Failed to download the file. Status code: {r.status_code}")

comp_row = find_best_header(df.iloc[:21])
head_rows = df.iloc[:(1+comp_row)]

rows_as_lists = [row.dropna().tolist() for _, row in head_rows.iterrows()]

tbl_title = rows_as_lists[0]

for i in range(len(rows_as_lists)):
     row = rows_as_lists[i]
     if any("rank" in str(cell).lower() for cell in row) and any("institution" in str(cell).lower() for cell in row):
        print(row)
        break

top_row = rows_as_lists[i]
second_row = rows_as_lists[i+1]
start_rec = df.iloc[(i+2):].copy()
col_na_cnt = start_rec.isna().sum(axis=0)
col_names = col_na_cnt[col_na_cnt>=len(start_rec)/2].index.tolist()

start_rec.drop(columns=col_names, inplace=True)

top_row_label = top_row[:3] + second_row
start_rec.columns = top_row_label

########## Need to find institution names with superscript
# Inst_names = start_rec['Institution']
# Inst_names[Inst_names.str.endswith(tuple(['a','b','c','d','e','f','g']))]

# choose object columns (strings) to convert
obj_cols = start_rec.iloc[:,1:].columns

# Remove everything except digits, dot and minus; 2) replace empty -> NaN; 3) convert
start_rec[obj_cols] = (
    start_rec[obj_cols]
    .astype(str)  # ensure string so replace works
    .replace(r'[^0-9\.\-]', '', regex=True)   # remove commas, $ signs, letters, etc.
    .replace('', np.nan)                      # empty -> NaN
    .apply(pd.to_numeric, errors='coerce')    # convert to numeric, invalid -> NaN
)


try:
    connection_string = (
        f"mariadb+mariadbconnector://{db_user}:{db_password}@"
        f"{db_host}:{db_port}/{db_name}"
    )
    # Create a dictionary with the SSL arguments
    ssl_args = {'ssl': True}
    # Pass this dictionary to the connect_args parameter
    engine = create_engine(
        connection_string,
        connect_args=ssl_args
    )
    print("SQLAlchemy engine created successfully.")
except Exception as e:
    print(f"Error creating engine: {e}")
    sys.exit(1)

conn = engine.connect()

#### Find relevant schools
inst_names = start_rec['Institution'].unique().tolist()
# Build one named placeholder per item
placeholders = [f":n{i}" for i in range(len(inst_names))]
in_clause = ", ".join(placeholders)
params = {f"n{i}": v for i, v in enumerate(inst_names)}
check_qry = text(f"SELECT inst_id, inst_name FROM institution WHERE inst_name IN ({in_clause})")
inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

# normalize by lower/strip
norm_inst = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_names]
norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_lookup['inst_name']]  

missing_inst = [orig for orig, norm in zip(inst_names, norm_inst) if norm not in set(norm_db)]

### Insert institution records
### UPDATE: need to check institution names
### U. South Floridad vs U. South Floridae

for i in range(len(missing_inst)):
    qry = text("INSERT INTO institution (inst_name, last_update) VALUES (:inst_name, :today_date)")
    record_to_insert = {"inst_name": missing_inst[i], "today_date": datetime.now()}
    conn.execute(qry, record_to_insert)
conn.commit()

inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)


#### Insert yearly funding records
col_exclude = ["Rank","All R&D expenditures"]
col_in_df = [c for c in start_rec.columns if c not in col_exclude]
df_sub = start_rec.loc[:,col_in_df]

# Get corresponding year
yearx = int(get_key_from_value(year_id_lookup, year_id))

for i in range(len(df_sub)):
    inst_x = df_sub.iloc[i,:]
    for j in range(1,df_sub.shape[1]):
        inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x['Institution'].lower()]['inst_id'].values
        check_qry = text("SELECT 1 FROM herd_fund_source WHERE year = :year AND inst_id = :inst_id_val AND fund_source = :fund_agency")
        check_result = conn.execute(check_qry, {"year": yearx, "inst_id_val": int(inst_id_val[0]), "fund_agency": inst_x.index[j]})
        if not check_result.fetchone():
            qry = text("INSERT INTO herd_fund_source (inst_id, year, fund_source, value) VALUES (:inst_id_val, :year, :fund_agency, :amount)")
            amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
            record_to_insert = {"inst_id_val": int(inst_id_val[0]), "year": yearx, "fund_agency": inst_x.index[j],"amount": amount}
            conn.execute(qry, record_to_insert)
conn.commit()
engine.dispose()
