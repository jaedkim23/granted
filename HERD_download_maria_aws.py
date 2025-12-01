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
import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into environment

# --- Connection Details ---
db_host = os.getenv('herd_host')
db_name = os.getenv('herd_database')
db_user = os.getenv('herd_username')
db_password = os.getenv('herd_password')
db_port = os.getenv('herd_port', 3306)  # Default to 3306 if not set

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

### Each year has a different 5-digit identifier
## https://ncses.nsf.gov/surveys/higher-education-research-development/2023#data

tabx_sub1 = "https://ncses.nsf.gov/pubs/nsf"
tabx_sub2 = "/assets/data-tables/tables/nsf"

year_id_lookup = 2023
year_id = get_year_id(year_id_lookup)

tabs = []

####################################################################################################
### Inserting/updating Table 21 data into database
### Table 21: Higher education R&D expenditures, ranked by R&D expenditures
tab21_link = tabx_dir1+str(year_id)+tabx_dir2+str(year_id)+"-tab021.xlsx"
tabs.append(tab21_link)

# The link should be of the file directly
url = tabs[0]

# Fetch file from URL
# df is the data frame read from URL address
r = requests.get(url)
if r.status_code == 200:
    excel_data= BytesIO(r.content)
    df = pd.read_excel(excel_data)
else:
     print(f"Failed to download the file. Status code: {r.status_code}")

# Find the likely header row
comp_row = find_best_header(df.iloc[:21])
head_rows = df.iloc[:(1+comp_row)]

# convert non-records into a list
rows_as_lists = [row.dropna().tolist() for _, row in head_rows.iterrows()]

# The first cell of file is the title of the table
tbl_title = rows_as_lists[0]

# Find "Institution" - header of Table 21
for i in range(len(rows_as_lists)):
     row = rows_as_lists[i]
     if any("rank" in str(cell).lower() for cell in row) and any("institution" in str(cell).lower() for cell in row):
        print(row)
        break

# Index i is the header row
top_row = rows_as_lists[i]

# Rest of data frame is the records
start_rec = df.iloc[(i+1):].copy()

# Table has extra columns between legitimate columns
# Find columns with more than half NaN values
col_na_cnt = start_rec.isna().sum(axis=0)
col_names = col_na_cnt[col_na_cnt>=len(start_rec)/2].index.tolist()

# Drop the unnecessary columns
start_rec.drop(columns= col_names, inplace=True)
start_rec.columns = top_row

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

#### Find relevant schools
inst_names = start_rec['Institution'].unique().tolist()
# Build one named placeholder per item
placeholders = [f":n{i}" for i in range(len(inst_names))]
in_clause = ", ".join(placeholders)
params = {f"n{i}": v for i, v in enumerate(inst_names)}
check_qry = text(f"SELECT inst_id, inst_name FROM institution WHERE inst_name IN ({in_clause})")
inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

########## Need to find institution names with superscript
inst_names_new, dup_inst = check_superscript_duplicates_single_list(inst_names)
inst_names_merged = remove_superscript_duplicates_two_lists(inst_names_new, inst_lookup['inst_name'].tolist())
inst_names = inst_names_merged[0]

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

# Get updated institution IDs
inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

#### Insert yearly funding records
all_numeric = all(isinstance(c, (int, float)) for c in start_rec.columns)
years_in_df = [c for c in start_rec.columns if isinstance(c, (int, float))]

# #### Check year to insert
# check_qry = text(f"SELECT UNIQUE(year) FROM herd_exp")
# exp_year_lookup = pd.read_sql_query(check_qry, con=engine, params=params)


years_in_df.insert(0, 'Institution')
df_sub = start_rec.loc[:,years_in_df]

for j in range(1,df_sub.shape[1]):
    yearx = df_sub.columns[j]
    df_year = df_sub[['Institution', yearx]]
    for i in range(len(df_year)):
        inst_x = df_year.iloc[i]['Institution']
        if inst_x.lower() == 'all institutions':
            continue
        inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x.lower()]['inst_id'].values
        check_qry = text("SELECT 1 FROM herd_exp WHERE year = :year AND inst_id = :inst_id_val")
        check_result = conn.execute(check_qry, {"year": yearx, "inst_id_val": int(inst_id_val[0])})

        if not check_result.fetchone():
            qry = text("INSERT INTO herd_exp (inst_id, year, value) VALUES (:inst_id_val, :year, :amount)")
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

####################################################################################################
### Inserting/updating Table 22 data into database
### Table 22: Higher education R&D expenditures, ranked by R&D expenditures, by source of funds

year_id_lookup = 2023
year_id = get_year_id(year_id_lookup)

tabs = []

### Table 22: Higher education R&D expenditures, ranked by R&D expenditures, by source of funds
tab22_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab022.xlsx"
tabs.append(tab22_link)

# The link should be of the file directly
url = tabs[0]

r = requests.get(url)
if r.status_code == 200:
    excel_data= BytesIO(r.content)
    df = pd.read_excel(excel_data)
else:
     print(f"Failed to download the file. Status code: {r.status_code}")

# Find the likely header row
comp_row = find_best_header(df.iloc[:21])
head_rows = df.iloc[:(1+comp_row)]

# convert non-records into a list
rows_as_lists = [row.dropna().tolist() for _, row in head_rows.iterrows()]

# The first cell of file is the title of the table
tbl_title = rows_as_lists[0]

# Find "Institution" - header of Table 22
for i in range(len(rows_as_lists)):
     row = rows_as_lists[i]
     if any("rank" in str(cell).lower() for cell in row) and any("institution" in str(cell).lower() for cell in row):
        print(row)
        break
     
# Index i is the header row
top_row = rows_as_lists[i]
second_row = rows_as_lists[i+1]

# Rest of data frame is the records
start_rec = df.iloc[(i+2):].copy()

# Table has extra columns between legitimate columns
# Find columns with more than half NaN values
col_na_cnt = start_rec.isna().sum(axis=0)
col_names = col_na_cnt[col_na_cnt>=len(start_rec)/2].index.tolist()

# Drop the unnecessary columns
start_rec.drop(columns=col_names, inplace=True)

# Combine top two header rows to get the correct header
top_row_label = top_row[:3] + second_row
start_rec.columns = top_row_label

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

########## Need to find institution names with superscript
inst_names_new, dup_inst = check_superscript_duplicates_single_list(inst_names)
inst_names_merged = remove_superscript_duplicates_two_lists(inst_names_new, inst_lookup['inst_name'].tolist())
inst_names = inst_names_merged[0]

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

# Get updated institution IDs
inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

#### Insert yearly funding records
col_exclude = ["Rank","All R&D expenditures"]
col_in_df = [c for c in start_rec.columns if c not in col_exclude]
df_sub = start_rec.loc[:,col_in_df]

### Check for any new sources of funding, update herd_fund_source_cat table if necessary
check_sources = update_fund_source_cat(col_in_df, engine)
if check_sources==1:
    print("New fund fields added to herd_fund_field table.")
else:
    print("No new fund fields.")

# Get corresponding year
yearx = int(get_key_from_value(year_id))

for i in range(len(df_sub)):
    inst_x = df_sub.iloc[i,:]
    for j in range(1,df_sub.shape[1]):
        source_name = df_sub.columns[j]
        source_name = source_name.strip().lower()
        get_source_id_qry = text("SELECT fund_source_id FROM herd_fund_source_cat WHERE lower(fund_source) = :source_input")
        source_id = pd.read_sql_query(get_source_id_qry, con=engine, params={"source_input": source_name})
        source_id = source_id['fund_source_id'].values[0]
        
        inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x['Institution'].lower()]['inst_id'].values
        
        check_qry = text("SELECT 1 FROM herd_fund_source WHERE year = :year AND inst_id = :inst_id_val AND fund_source_id = :fund_agency")
        check_result = conn.execute(check_qry, {"year": yearx, "inst_id_val": int(inst_id_val[0]), "fund_agency": source_id})
        if not check_result.fetchone():
            qry = text("INSERT INTO herd_fund_source (inst_id, fund_source_id, year, value) VALUES (:inst_id_val, :fund_agency, :year, :amount)")
            amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
            record_to_insert = {"inst_id_val": int(inst_id_val[0]), "fund_agency": source_id, "year": yearx, "amount": amount}
            conn.execute(qry, record_to_insert)
conn.commit()
engine.dispose()


####################################################################################################
### Inserting/updating Table 23 data into database
### Table 23: Higher education R&D expenditures, ranked by all R&D expenditures

year_id_lookup = 2021
year_id = get_year_id(year_id_lookup)

tabs = []

### Table 23: Higher education R&D expenditures, ranked by all R&D expenditures, by R&D field
tab23_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab023.xlsx"
tabs.append(tab23_link)

# The link should be of the file directly
url = tabs[0]

# Table 23
r = requests.get(url)
if r.status_code == 200:
    excel_data= BytesIO(r.content)
    df = pd.read_excel(excel_data)
else:
     print(f"Failed to download the file. Status code: {r.status_code}")

# Find the likely header row
comp_row = find_best_header(df.iloc[:5])
head_rows = df.iloc[:(1+comp_row)]

# convert non-records into a list
rows_as_lists = [row.dropna().tolist() for _, row in head_rows.iterrows()]

# The first cell of file is the title of the table
tbl_title = rows_as_lists[0]

# Find "Institution" - header of Table 23
for i in range(len(rows_as_lists)):
     row = rows_as_lists[i]
     if any("rank" in str(cell).lower() for cell in row) and any("institution" in str(cell).lower() for cell in row):
        print(row)
        break
     
# Index i is the header row
top_row = rows_as_lists[i]

# Rest of data frame is the records
start_rec = df.iloc[(i+1):].copy()

# Table has extra columns between legitimate columns
# Find columns with more than half NaN values
col_na_cnt = start_rec.isna().sum(axis=0)
col_names = col_na_cnt[col_na_cnt>=len(start_rec)/2].index.tolist()

# Drop the unnecessary columns
start_rec.drop(columns=col_names, inplace=True)

# Assign header
start_rec.columns = top_row

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

########## Need to find institution names with superscript
inst_names_new, dup_inst = check_superscript_duplicates_single_list(inst_names)
inst_names_merged = remove_superscript_duplicates_two_lists(inst_names_new, inst_lookup['inst_name'].tolist())
inst_names = inst_names_merged[0]

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

# Get updated institution IDs
inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

#### Insert yearly funding records
col_exclude = ["Rank","All R&D expenditures"]
col_in_df = [c for c in start_rec.columns if c not in col_exclude]
df_sub = start_rec.loc[:,col_in_df]

#### Check for any new R&D fields, update herd_fund_field table if necessary
check_fields = update_fund_field(col_in_df, engine)
if check_fields==1:
    print("New fund fields added to herd_fund_field table.")
else:
    print("No new fund fields.")
    
# Get corresponding year
yearx = int(get_key_from_value( year_id))

for i in range(len(df_sub)):
    inst_x = df_sub.iloc[i,:]
    for j in range(1,df_sub.shape[1]):
        field_name = df_sub.columns[j]
        field_name = field_name.strip().lower()    
        get_field_id_qry = text("SELECT field_id FROM herd_field WHERE field_name = :field_input")
        
        field_id = pd.read_sql_query(get_field_id_qry, con=engine, params={"field_input": field_name})
        field_id = field_id['field_id'].values[0]
        inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x['Institution'].lower()]['inst_id'].values
        
        check_qry = text("SELECT 1 FROM herd_fund_field WHERE year = :year AND inst_id = :inst_id_val AND field_id = :field")
        check_result = conn.execute(check_qry, {"year": yearx, "inst_id_val": int(inst_id_val[0]), "field": int(field_id)})
        if not check_result.fetchone():
            qry = text("INSERT INTO herd_fund_field (inst_id, field_id, year, value) VALUES (:inst_id_val, :field_id_in, :year, :amount)")
            amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
            record_to_insert = {"inst_id_val": int(inst_id_val[0]), "field_id_in": int(field_id), "year": yearx, "amount": amount}
            conn.execute(qry, record_to_insert)
conn.commit()
engine.dispose()


####################################################################################################
### Inserting/updating Table 79 data into database
### Table 79: Headcount and FTEs of R&D personnel at higher education institutions, by state, institutional control, institution, and personnel function
year_id_lookup = {'2023': 25314, '2022': 24308, '2021': 23304}

"""
This table started in 2023!!!!
"""
year_id = year_id_lookup['2023']

tabs = []

### Table 79: Headcount and FTEs of R&D personnel at higher education institutions, by state, institutional control, institution, and personnel function
tab79_link = tabx_dir1+str(year_id)+tabx_dir2+str(year_id)+"-tab079.xlsx"
tabs.append(tab79_link)

# The link should be of the file directly
url = tabs[0]

# Fetch file from URL
# df is the data frame read from URL address
r = requests.get(url)
if r.status_code == 200:
    excel_data= BytesIO(r.content)
    df = pd.read_excel(excel_data)
else:
     print(f"Failed to download the file. Status code: {r.status_code}")

# Find the likely header row
comp_row = find_best_header(df.iloc[:5])
head_rows = df.iloc[:(1+comp_row)]

# convert non-records into a list
rows_as_lists = [row.dropna().tolist() for _, row in head_rows.iterrows()]

# The first cell of file is the title of the table
tbl_title = rows_as_lists[0]

# Find "Institution" - header of Table 79
for i in range(len(rows_as_lists)):
     row = rows_as_lists[i]
     if any("institutional control" in str(cell).lower() for cell in row) and any("and institution" in str(cell).lower() for cell in row):
        print(row)
        break
     
# Index i is the header row
top_row = rows_as_lists[i]
second_row = rows_as_lists[i+1]

# Rest of data frame is the records
start_rec = df.iloc[(i+2):].copy()

# Table has extra columns between legitimate columns
# Find columns with more than half NaN values
col_na_cnt = start_rec.isna().sum(axis=0)
col_names = col_na_cnt[col_na_cnt>=len(start_rec)/2].index.tolist()

col_names_imputed_cnt = (start_rec=="i").sum(axis=0)
col_names_imputed = col_names_imputed_cnt[col_names_imputed_cnt>0].index.tolist()

col_names_merge = [col for col in col_names if col in col_names_imputed]

# Drop the unnecessary columns
start_rec.drop(columns=col_names, inplace=True)

### Connect to database
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

# link categories to field names
col_x = top_row[1:]

#### Check for any new R&D fields, update herd_fund_field table if necessary
check_cat = update_headcount_cat(col_x, engine)
if check_cat==1:
    print("New headcount category added to herd_headcount_cat table.")
else:
    print("No new headcount category.")

headcount_counter = 0
fte_counter = 0
for idx in range(len(second_row)):
    if second_row[idx]=="Headcount":
        cat_check_qry = text(f"SELECT headcount_cat_id FROM herd_headcount_cat WHERE headcount_cat = '{col_x[headcount_counter]}'")
        cat_id_found = pd.read_sql_query(cat_check_qry, con=engine)
        cat_id_found = cat_id_found['headcount_cat_id'][0]
        second_row[idx] = second_row[idx] + "_" + str(cat_id_found)
        headcount_counter += 1
    elif second_row[idx]=="FTEs":
        cat_check_qry = text(f"SELECT headcount_cat_id FROM herd_headcount_cat WHERE headcount_cat = '{col_x[fte_counter]}'")
        cat_id_found = pd.read_sql_query(cat_check_qry, con=engine)
        cat_id_found = cat_id_found['headcount_cat_id'][0]
        second_row[idx] = second_row[idx] + "_" + str(cat_id_found)
        fte_counter += 1
    
# Assign header
start_rec.columns = ["Item"]+second_row

# Remove everything except digits, dot and minus; 2) replace empty -> NaN; 3) convert
for j in range(1, start_rec.shape[1]):  # skip first column (index 0)
    start_rec.iloc[:, j] = (
        start_rec.iloc[:, j]
        .astype(str)
        .str.replace(r'[^0-9]', '', regex=True)
        .replace('', np.nan)
        .apply(pd.to_numeric, errors='coerce')
    )

#### Find relevant schools
inst_names = start_rec['Item'].unique().tolist()
# Build one named placeholder per item
placeholders = [f":n{i}" for i in range(len(inst_names))]
in_clause = ", ".join(placeholders)
params = {f"n{i}": v for i, v in enumerate(inst_names)}
check_qry = text(f"SELECT inst_id, inst_name FROM institution WHERE inst_name IN ({in_clause})")
inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

inst_names_new, dup_inst = check_superscript_duplicates_single_list(inst_names)
inst_names_merged = remove_superscript_duplicates_two_lists(inst_names_new, inst_lookup['inst_name'].tolist())
inst_names = inst_names_merged[0]

# normalize by lower/strip
norm_inst = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_names]
norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_lookup['inst_name']]  

missing_inst = [orig for orig, norm in zip(inst_names, norm_inst) if norm not in set(norm_db)]

####################################
### Initial insert of states into herd_state table
"""
states = ['United States', 'Alabama', 'Public', 'Private', 'Alaska', 'Arizona', 'Arkansas', 'California', 
          'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Hawaii', 
          'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 
          'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 
          'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 
          'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 
          'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 
          'Wyoming', 'Guam', 'Puerto Rico', 'Virgin Islands']
for i in range(len(states)):
    qry = text("INSERT INTO herd_state (state_name, last_update) VALUES (:state, :today_date)")
    record_to_insert = {"state": states[i], "today_date": datetime.now()}
    conn.execute(qry, record_to_insert)
conn.commit()
"""
########################################

check_state_qry = text(f"SELECT state_name FROM herd_state")
state_lookup = pd.read_sql_query(check_state_qry, con=engine)
state_lookup = state_lookup['state_name'].tolist()
missing_inst = [inst for inst in missing_inst if inst not in state_lookup]

### Insert institution records
### UPDATE: need to check institution names
### U. South Floridad vs U. South Floridae

for i in range(len(missing_inst)):
    qry = text("INSERT INTO institution (inst_name, last_update) VALUES (:inst_name, :today_date)")
    record_to_insert = {"inst_name": missing_inst[i], "today_date": datetime.now()}
    conn.execute(qry, record_to_insert)
conn.commit()

# Get updated institution IDs
inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

# Get updated state IDs
state_lookup = pd.read_sql_query(check_state_qry, con=engine)

#### Insert yearly funding records
df_sub = start_rec.copy()

# Get corresponding year
yearx = int(get_key_from_value( year_id))
state_rec = 0
for i in range(len(df_sub)):
    inst_x = df_sub.iloc[i,:]
    # Check if record is institutiton or state
    inst_check_qry = text("SELECT 1 FROM institution WHERE lower(inst_name) = :inst_name")
    inst_check_result = conn.execute(inst_check_qry, {"inst_name": inst_x['Item'].lower()})
    if not inst_check_result.fetchone():
        state_check_qry = text(f"SELECT state_id FROM herd_state WHERE lower(state_name) = '{inst_x['Item'].lower()}'")
        state_id_found = pd.read_sql_query(state_check_qry, con=engine)
        state_id_found = state_id_found['state_id'][0]
        state_rec = 1
    else:
        inst_check_qry = text(f'SELECT inst_id FROM institution WHERE lower(inst_name) = "{inst_x['Item'].lower()}"')
        inst_id_found = pd.read_sql_query(inst_check_qry, con=engine)
        inst_id_found = inst_id_found['inst_id'][0]
        state_rec = 0
    for j in range(1,df_sub.shape[1]):
        field_name = df_sub.columns[j]
        cat_id_check = field_name.split("_")[1]
        if field_name.split("_")[0].lower()=="headcount":
            fte_field = 0
        else:
            fte_field = 1
        
        if state_rec == 1:
            hcnt_qry = text("INSERT INTO herd_headcount_state (headcount_cat_id, state_id, fte, year, value) VALUES (:cat_id_val, :state_id_val, :fte_val, :year_val, :amount)")
            amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
            record_to_insert = {"cat_id_val": int(cat_id_check), "state_id_val": int(state_id_found), "fte_val": int(fte_field), "year_val": yearx, "amount": amount}
            conn.execute(hcnt_qry, record_to_insert)
        else:
            hcnt_qry = text("INSERT INTO herd_headcount (headcount_cat_id, inst_id, fte, year, value) VALUES (:cat_id_val, :inst_id_val, :fte_val, :year_val, :amount)")
            amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
            record_to_insert = {"cat_id_val": int(cat_id_check), "inst_id_val": int(inst_id_found), "fte_val": int(fte_field), "year_val": yearx, "amount": amount}
            conn.execute(hcnt_qry, record_to_insert)
conn.commit()
engine.dispose()

