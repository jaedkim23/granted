"""
HERD Data Processing Script 
Downloads and processes Higher Education R&D expenditure data from NSF NCSES
Handles Tables 21, 22, 23, and 79 from the HERD survey data

Author: USD ResDataNexus Team
Last Updated: 2026-03-18
By: Jae Kim
"""

from datetime import datetime
import re
import requests
import pandas as pd
import numpy as np
from io import BytesIO
from HERD_functions import *
from sqlalchemy import create_engine, text
import sys
import os
from dotenv import load_dotenv

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load environment variables from .env file
load_dotenv()


# Database connection credentials
DB_CONFIG = {
    'host': os.getenv('herd_host_test'),
    'database': os.getenv('herd_database_test'),
    'user': os.getenv('herd_username_test'),
    'password': os.getenv('herd_password_test'),
    'port': os.getenv('herd_port_test', 3306)
}

#for local connection
# # Database connection credentials
# DB_CONFIG = {
#     'host': os.getenv('herd_host_local'),
#     'database': os.getenv('herd_database_local'),
#     'user': os.getenv('herd_username_local'),
#     'password': os.getenv('herd_password_local'),
#     'port': os.getenv('herd_port_local', 3306)
# }


# NSF data URL templates
TABX_DIR1 = "https://ncses.nsf.gov/pubs/nsf"
TABX_DIR2 = "/assets/data-tables/tables/nsf"


# ============================================================================
# DATABASE CONNECTION FUNCTIONS
# ============================================================================

def create_db_engine():
    """
    Create SQLAlchemy database engine with SSL connection.

    Returns:
        engine: SQLAlchemy engine object configured for MariaDB with SSL

    Raises:
        SystemExit: If engine creation fails
    """
    try:
        connection_string = (
            f"mariadb+mariadbconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        ssl_args = {'ssl': True}
        engine = create_engine(connection_string, connect_args=ssl_args)
        print("SQLAlchemy engine created successfully.")
        return engine
    except Exception as e:
        print(f"Error creating engine: {e}")
        sys.exit(1)

# ============================================================================
# DATA DOWNLOAD AND PARSING FUNCTIONS
# ============================================================================
def build_table_url(year_id, table_number):
    """
    Construct NSF data table URL.

    Args:
        year_id (int): NSF year identifier (e.g., 25314 for 2023)
        table_number (int): Table number (21, 22, 23, 79)

    Note: Each year has a different 5-digit identifier

    Returns:
        Complete URL to Excel file
    """
    table_str = f"{table_number:03d}"  # Format as 3-digit number with leading zeros
    return f"{TABX_DIR1}{year_id}{TABX_DIR2}{year_id}-tab{table_str}.xlsx"

def download_excel_from_url(url):
    """
    Download Excel file from URL and load into pandas DataFrame.

    Args:
        url (str): URL of the Excel file

    Returns:
        df: pandas DataFrame containing the Excel data

    Raises:
        SystemExit: If download fails
    """
    r = requests.get(url)
    if r.status_code == 200:
        excel_data = BytesIO(r.content)
        df = pd.read_excel(excel_data)
        print(f"Successfully downloaded data from URL")
        return df
    else:
        print(f"Failed to download the file. Status code: {r.status_code}")
        sys.exit(1)

def parse_excel_headers(df, search_terms, max_rows=21):
    """
    Parse Excel file to find header row and extract metadata.

    Args:
        df: raw pandas DataFrame from Excel file
        search_terms: list of terms to identify the header row
        max_rows: maximum rows to search for header

    Returns:
        tuple: (header_row_index, title, rows_as_lists)
            header_row_index: Index of the header row
            title: Table title from first row
            rows_as_lists: All header rows as lists
    """
    # Find the likely header row based on non-null count
    comp_row = find_best_header(df.iloc[:max_rows])
    head_rows = df.iloc[:(1+comp_row)]

    # Convert header rows to list format
    rows_as_lists = [row.dropna().tolist() for _, row in head_rows.iterrows()]
    tbl_title = rows_as_lists[0]

    # Find the actual header row based on search terms
    for i in range(len(rows_as_lists)):
        row = rows_as_lists[i]
        if all(any(term in str(cell).lower() for cell in row) for term in search_terms):
            print(f"Found header row at index {i}")
            return i, tbl_title, rows_as_lists

    raise ValueError(f"Could not find header row with terms: {search_terms}")

# ============================================================================
# DATA CLEANING FUNCTIONS
# ============================================================================

def clean_dataframe_columns(df):
    """
    Remove columns with more than 50% NaN values.
    These are typically formatting columns in NSF Excel files.

    Args:
        df: pandas DataFrame - converted from downloaded Excel table

    Returns:
        df_cleaned: pandas DataFrame with sparse columns removed
    """
    col_na_cnt = df.isna().sum(axis=0)
    col_names = col_na_cnt[col_na_cnt >= len(df)/2].index.tolist()
    df_cleaned = df.drop(columns=col_names)
    print(f"Removed {len(col_names)} sparse columns")
    return df_cleaned


def convert_currency_columns_to_numeric(df, exclude_first_col=True):
    """
    Convert currency/numeric columns from string to numeric format.
    Removes commas, dollar signs, and other non-numeric characters.

    Args:
        df: pandas DataFrame 
        exclude_first_col: Whether to exclude first column (typically institution names)

    Returns:
        df: pandas DataFrame with numeric columns converted
    """
    if exclude_first_col:
        obj_cols = df.iloc[:, 1:].columns
    else:
        obj_cols = df.columns

    df[obj_cols] = (
        df[obj_cols]
        .astype(str)
        .replace(r'[^0-9\.\-]', '', regex=True)  # Keep only digits, dots, minus
        .replace('', np.nan)
        .apply(pd.to_numeric, errors='coerce')
    )

    return df

# ============================================================================
# INSTITUTION MANAGEMENT FUNCTIONS
# ============================================================================

def get_or_create_institutions(inst_names, engine):
    """
    Check for institutions in database and insert missing ones.
    Handles superscript duplicates and normalizes institution names.

    Args:
        inst_names: List of institution names from data file
        engine: SQLAlchemy engine

    Returns:
        inst_lookup: pandas DataFrame: Institution lookup table with inst_id and inst_name
    """
    conn = engine.connect()

    # Build parameterized query to check existing institutions
    placeholders = [f":n{i}" for i in range(len(inst_names))]
    in_clause = ", ".join(placeholders)
    params = {f"n{i}": v for i, v in enumerate(inst_names)}
    check_qry = text(f"SELECT inst_id, inst_name FROM institution WHERE inst_name IN ({in_clause})")
    inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

    # Handle superscript duplicates (e.g., "University of XYZ" vs "University of XYZ¹")
    inst_names_new, dup_inst = check_superscript_duplicates_single_list(inst_names)
    inst_names_merged = remove_superscript_duplicates_two_lists(inst_names_new, inst_lookup['inst_name'].tolist())
    inst_names = inst_names_merged[0]

    # Normalize names for comparison (lowercase, strip whitespace)
    norm_inst = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_names]
    norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_lookup['inst_name']]

    # Find institutions not in database
    missing_inst = [orig for orig, norm in zip(inst_names, norm_inst) if norm not in set(norm_db)]

    # Insert missing institutions
    if missing_inst:
        for inst_name in missing_inst:
            qry = text("INSERT INTO institution (inst_name, last_update) VALUES (:inst_name, :today_date)")
            record_to_insert = {"inst_name": inst_name, "today_date": datetime.now()}
            conn.execute(qry, record_to_insert)
        conn.commit()
        print(f"Inserted {len(missing_inst)} new institutions")

        # Refresh lookup table with newly inserted institutions
        inst_lookup = pd.read_sql_query(check_qry, con=engine, params=params)

    conn.close()
    return inst_lookup

# ============================================================================
# DATA INSERTION FUNCTIONS - TABLE 21 (TABLE 13 in 2024)
# ============================================================================

def insert_expenditure_data(df, inst_lookup, engine):
    """
    Insert R&D expenditure data into herd_exp table.
    Handles multiple years of expenditure data per institution.

    Args:
        df: pandas DataFrame with 'Institution' column and year columns (numeric)
        inst_lookup: Institution lookup table (pandas DataFrame) with inst_id and inst_name
        engine: SQLAlchemy engine
    
    Return:
        None - message to indicate the number of rows inserted
    """
    conn = engine.connect()

    # Identify year columns (columns with numeric names)
    years_in_df = [c for c in df.columns if isinstance(c, (int, float))]
    years_in_df.insert(0, 'Institution')
    df_sub = df.loc[:, years_in_df]

    inserted_count = 0

    # Insert data for each year
    for j in range(1, df_sub.shape[1]):
        yearx = df_sub.columns[j]
        df_year = df_sub[['Institution', yearx]]

        for i in range(len(df_year)):
            inst_x = df_year.iloc[i]['Institution']

            # Skip aggregate rows
            if inst_x.lower() == 'all institutions':
                continue

            # Get institution ID
            inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x.lower()]['inst_id'].values
            if len(inst_id_val) == 0:
                print(f"Warning: Institution '{inst_x}' not found in lookup table")
                continue
            
            
            # compute new value once
            amount = None if pd.isna(float(df_year.iloc[i, 1])) else float(df_year.iloc[i, 1])

            # get existing value (if any)
            check_qry = text("""
                SELECT value
                FROM herd_exp
                WHERE year = :year AND inst_id = :inst_id_val
            """)
            row = conn.execute(check_qry, {"year": yearx, "inst_id_val": int(inst_id_val[0])}).fetchone()

            if row is None:
                # INSERT if missing
                qry = text("INSERT INTO herd_exp (inst_id, year, value) VALUES (:inst_id_val, :year, :amount)")
                conn.execute(qry, {"inst_id_val": int(inst_id_val[0]), "year": yearx, "amount": amount})
                inserted_count += 1
            else:
                existing_value = row[0]
                # UPDATE if different (handles revisions)
                if existing_value != amount:
                    print(
                    f"UPDATE DETECTED → inst={inst_x}, "
                    f"year={yearx}, "
                    f"old_value={existing_value}, "
                    f"new_value={amount}")


                    upd = text("""
                        UPDATE herd_exp
                        SET value = :amount
                        WHERE year = :year AND inst_id = :inst_id_val
                    """)
                    conn.execute(upd, {"amount": amount, "year": yearx, "inst_id_val": int(inst_id_val[0])})


            # # Check if record already exists
            # check_qry = text("SELECT 1 FROM herd_exp WHERE year = :year AND inst_id = :inst_id_val")
            # check_result = conn.execute(check_qry, {"year": yearx, "inst_id_val": int(inst_id_val[0])})

            # # Insert if not exists
            # if not check_result.fetchone():
            #     qry = text("INSERT INTO herd_exp (inst_id, year, value) VALUES (:inst_id_val, :year, :amount)")
            #     amount = None if pd.isna(float(df_year.iloc[i, 1])) else float(df_year.iloc[i, 1])
            #     record_to_insert = {"inst_id_val": int(inst_id_val[0]), "year": yearx, "amount": amount}
            #     conn.execute(qry, record_to_insert)
            #     inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted_count} expenditure records across {len(years_in_df)-1} years")


def insert_ranking_data(df, inst_lookup, year, engine):
    """
    Insert R&D ranking data into herd_rank table.

    Args:
        df: pandas DataFrame with 'Institution' and 'Rank' columns
        inst_lookup: Institution lookup table
        year: Year for the ranking data
        engine: SQLAlchemy engine
    """
    conn = engine.connect()

    # Filter to rows with ranking data
    rank_year_df = df.loc[:, ['Institution', 'Rank']]
    rank_year_df = rank_year_df[~rank_year_df['Rank'].isna()]

    inserted_count = 0

    for i in range(len(rank_year_df)):
        inst_x = rank_year_df.iloc[i]['Institution']
        inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x.lower()]['inst_id'].values

        if len(inst_id_val) == 0:
            print(f"Warning: Institution '{inst_x}' not found in lookup table")
            continue

        # Check if record already exists
        check_qry = text("SELECT 1 FROM herd_rank WHERE year = :year AND inst_id = :inst_id_val")
        check_result = conn.execute(check_qry, {"year": year, "inst_id_val": int(inst_id_val[0])})

        # Insert if not exists
        if not check_result.fetchone():
            qry = text("INSERT INTO herd_rank (inst_id, year, rank) VALUES (:inst_id_val, :year, :val)")
            rank = None if pd.isna(float(rank_year_df.iloc[i, 1])) else float(rank_year_df.iloc[i, 1])
            record_to_insert = {"inst_id_val": int(inst_id_val[0]), "year": year, "val": rank}
            conn.execute(qry, record_to_insert)
            inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted_count} ranking records")

def process_table_21(year_lookup):
    """
    Process Table 21: Higher education R&D expenditures, ranked by R&D expenditures.

    Args:
        year_lookup: year to process (e.g., 2023)
    """
    print(f"\n{'='*80}")
    print(f"Processing Table 21 for year {year_lookup}")
    print(f"{'='*80}\n")

    # Get year ID and build URL
    year_id = get_year_id(year_lookup)
    url = build_table_url(year_id, 21)

    # Download and parse Excel file
    df = download_excel_from_url(url)
    header_idx, title, rows_as_lists = parse_excel_headers(df, ["rank", "institution"])

    # Extract header and data
    top_row = rows_as_lists[header_idx]
    start_rec = df.iloc[(header_idx + 1):].copy()

    # Clean and prepare data
    start_rec = clean_dataframe_columns(start_rec)
    start_rec.columns = top_row
    start_rec = convert_currency_columns_to_numeric(start_rec)

    # Database operations
    engine = create_db_engine()
    inst_names = start_rec['Institution'].unique().tolist()
    inst_lookup = get_or_create_institutions(inst_names, engine)

    # Insert expenditure and ranking data
    insert_expenditure_data(start_rec, inst_lookup, engine)

    years_in_df = [c for c in start_rec.columns if isinstance(c, (int, float))]
    rank_year = max(years_in_df)
    insert_ranking_data(start_rec, inst_lookup, rank_year, engine)

    engine.dispose()
    print(f"Table 21 processing complete\n")

# ============================================================================
# DATA INSERTION FUNCTIONS - TABLE 22 (TABLE 14 in 2024)
# ============================================================================

def insert_funding_source_data(df, inst_lookup, year, engine):
    """
    Insert R&D funding by source data into herd_fund_source table.

    Args:
        df (pd.DataFrame): DataFrame with 'Institution' column and funding source columns
        inst_lookup (pd.DataFrame): Institution lookup table
        year (int): Year for the data
        engine: SQLAlchemy engine
    """
    conn = engine.connect()

    # Exclude metadata columns
    col_exclude = ["Rank", "All R&D expenditures"]
    col_in_df = [c for c in df.columns if c not in col_exclude]
    df_sub = df.loc[:, col_in_df]

    # Update fund source categories if new sources found
    check_sources = update_fund_source_cat(col_in_df, engine)
    if check_sources == 1:
        print("New fund sources added to herd_fund_source_cat table")
    else:
        print("No new fund sources found")

    inserted_count = 0

    # Insert data for each institution and funding source
    for i in range(len(df_sub)):
        inst_x = df_sub.iloc[i, :]

        for j in range(1, df_sub.shape[1]):
            source_name = df_sub.columns[j].strip().lower()

            # Get funding source ID
            get_source_id_qry = text("SELECT fund_source_id FROM herd_fund_source_cat WHERE lower(fund_source) = :source_input")
            source_id = pd.read_sql_query(get_source_id_qry, con=engine, params={"source_input": source_name})
            source_id = source_id['fund_source_id'].values[0]

            # Get institution ID
            inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x['Institution'].lower()]['inst_id'].values

            if len(inst_id_val) == 0:
                continue

            # Check if record already exists
            check_qry = text("SELECT 1 FROM herd_fund_source WHERE year = :year AND inst_id = :inst_id_val AND fund_source_id = :fund_agency")
            check_result = conn.execute(check_qry, {"year": year, "inst_id_val": int(inst_id_val[0]), "fund_agency": source_id})

            # Insert if not exists
            if not check_result.fetchone():
                qry = text("INSERT INTO herd_fund_source (inst_id, fund_source_id, year, value) VALUES (:inst_id_val, :fund_agency, :year, :amount)")
                amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
                record_to_insert = {"inst_id_val": int(inst_id_val[0]), "fund_agency": source_id, "year": year, "amount": amount}
                conn.execute(qry, record_to_insert)
                inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted_count} funding source records")


# ============================================================================
# DATA INSERTION FUNCTIONS - TABLE 23 (TABLE 15 in 2024)
# ============================================================================

def insert_funding_field_data(df, inst_lookup, year, engine):
    """
    Insert R&D funding by field data into herd_fund_field table.

    Args:
        df (pd.DataFrame): DataFrame with 'Institution' column and field columns
        inst_lookup (pd.DataFrame): Institution lookup table
        year (int): Year for the data
        engine: SQLAlchemy engine
    """
    conn = engine.connect()

    # Exclude metadata columns
    col_exclude = ["Rank", "All R&D expenditures"]
    col_in_df = [c for c in df.columns if c not in col_exclude]
    df_sub = df.loc[:, col_in_df]

    # Update R&D field categories if new fields found
    check_fields = update_fund_field(col_in_df, engine)
    if check_fields == 1:
        print("New fund fields added to herd_fund_field table")
    else:
        print("No new fund fields found")

    inserted_count = 0

    # Insert data for each institution and R&D field
    for i in range(len(df_sub)):
        inst_x = df_sub.iloc[i, :]

        for j in range(1, df_sub.shape[1]):
            field_name = df_sub.columns[j].strip().lower()

            # Get field ID
            get_field_id_qry = text("SELECT field_id FROM herd_field WHERE field_name = :field_input")
            field_id = pd.read_sql_query(get_field_id_qry, con=engine, params={"field_input": field_name})
            field_id = field_id['field_id'].values[0]

            # Get institution ID
            inst_id_val = inst_lookup[inst_lookup['inst_name'].str.lower() == inst_x['Institution'].lower()]['inst_id'].values

            if len(inst_id_val) == 0:
                continue

            # Check if record already exists
            check_qry = text("SELECT 1 FROM herd_fund_field WHERE year = :year AND inst_id = :inst_id_val AND field_id = :field")
            check_result = conn.execute(check_qry, {"year": year, "inst_id_val": int(inst_id_val[0]), "field": int(field_id)})

            # Insert if not exists
            if not check_result.fetchone():
                qry = text("INSERT INTO herd_fund_field (inst_id, field_id, year, value) VALUES (:inst_id_val, :field_id_in, :year, :amount)")
                amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
                record_to_insert = {"inst_id_val": int(inst_id_val[0]), "field_id_in": int(field_id), "year": year, "amount": amount}
                conn.execute(qry, record_to_insert)
                inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted_count} funding field records")


# ============================================================================
# DATA INSERTION FUNCTIONS - TABLE 79 (TABLE 27 in 2024)
# ============================================================================

def insert_headcount_data(df, inst_lookup, state_lookup, year, engine):
    """
    Insert headcount and FTE data into herd_headcount and herd_headcount_state tables.

    Args:
        df (pd.DataFrame): DataFrame with headcount/FTE data
        inst_lookup (pd.DataFrame): Institution lookup table
        state_lookup (pd.DataFrame): State lookup table
        year (int): Year for the data
        engine: SQLAlchemy engine
    """
    conn = engine.connect()
    inserted_count = 0

    # Process each row (institution or state)
    for i in range(len(df)):
        inst_x = df.iloc[i, :]

        # Determine if row is institution or state
        inst_check_qry = text("SELECT 1 FROM institution WHERE lower(inst_name) = :inst_name")
        inst_check_result = conn.execute(inst_check_qry, {"inst_name": inst_x['Item'].lower()})

        if not inst_check_result.fetchone():
            # This is a state record
            state_check_qry = text(f"SELECT state_id FROM herd_state WHERE lower(state_name) = '{inst_x['Item'].lower()}'")
            state_id_found = pd.read_sql_query(state_check_qry, con=engine)
            state_id_found = state_id_found['state_id'][0]
            is_state_rec = True
        else:
            # This is an institution record
            inst_check_qry = text(f'SELECT inst_id FROM institution WHERE lower(inst_name) = "{inst_x['Item'].lower()}"')
            inst_id_found = pd.read_sql_query(inst_check_qry, con=engine)
            inst_id_found = inst_id_found['inst_id'][0]
            is_state_rec = False

        # Process each column (headcount category)
        for j in range(1, df.shape[1]):
            field_name = df.columns[j]
            cat_id_check = field_name.split("_")[1]

            # Determine if FTE or headcount
            fte_field = 1 if field_name.split("_")[0].lower() == "ftes" else 0

            # Insert into appropriate table
            if is_state_rec:
                hcnt_qry = text("INSERT INTO herd_headcount_state (headcount_cat_id, state_id, fte, year, value) VALUES (:cat_id_val, :state_id_val, :fte_val, :year_val, :amount)")
                amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
                record_to_insert = {"cat_id_val": int(cat_id_check), "state_id_val": int(state_id_found), "fte_val": int(fte_field), "year_val": year, "amount": amount}
                conn.execute(hcnt_qry, record_to_insert)
            else:
                hcnt_qry = text("INSERT INTO herd_headcount (headcount_cat_id, inst_id, fte, year, value) VALUES (:cat_id_val, :inst_id_val, :fte_val, :year_val, :amount)")
                amount = None if pd.isna(float(inst_x.iloc[j])) else float(inst_x.iloc[j])
                record_to_insert = {"cat_id_val": int(cat_id_check), "inst_id_val": int(inst_id_found), "fte_val": int(fte_field), "year_val": year, "amount": amount}
                conn.execute(hcnt_qry, record_to_insert)

            inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted_count} headcount/FTE records")


# ============================================================================
# TABLE PROCESSING ORCHESTRATION FUNCTIONS
# ============================================================================

def process_table_21(year_lookup):
    """
    Process Table 21: Higher education R&D expenditures, ranked by R&D expenditures.

    Args:
        year_lookup (int): Year to process (e.g., 2023)
    """
    print(f"\n{'='*80}")
    print(f"Processing Table 21 for year {year_lookup}")
    print(f"{'='*80}\n")

    # Get year ID and build URL
    year_id = get_year_id(year_lookup)
    url = build_table_url(year_id, 21)

    # Download and parse Excel file
    df = download_excel_from_url(url)
    header_idx, title, rows_as_lists = parse_excel_headers(df, ["rank", "institution"])

    # Extract header and data
    top_row = rows_as_lists[header_idx]
    start_rec = df.iloc[(header_idx + 1):].copy()

    # Clean and prepare data
    start_rec = clean_dataframe_columns(start_rec)
    start_rec.columns = top_row
    start_rec = convert_currency_columns_to_numeric(start_rec)

    # Database operations
    engine = create_db_engine()
    inst_names = start_rec['Institution'].unique().tolist()
    inst_lookup = get_or_create_institutions(inst_names, engine)

    # Insert expenditure and ranking data
    insert_expenditure_data(start_rec, inst_lookup, engine)

    years_in_df = [c for c in start_rec.columns if isinstance(c, (int, float))]
    rank_year = max(years_in_df)
    insert_ranking_data(start_rec, inst_lookup, rank_year, engine)

    engine.dispose()
    print(f"Table 21 processing complete\n")


def process_table_22(year_lookup):
    """
    Process Table 22: Higher education R&D expenditures by source of funds.

    Args:
        year_lookup (int): Year to process (e.g., 2023)
    """
    print(f"\n{'='*80}")
    print(f"Processing Table 22 for year {year_lookup}")
    print(f"{'='*80}\n")

    # Get year ID and build URL
    year_id = get_year_id(year_lookup)
    url = build_table_url(year_id, 22)

    # Download and parse Excel file
    df = download_excel_from_url(url)
    header_idx, title, rows_as_lists = parse_excel_headers(df, ["rank", "institution"])

    # Extract two-row header
    top_row = rows_as_lists[header_idx]
    second_row = rows_as_lists[header_idx + 1]
    start_rec = df.iloc[(header_idx + 2):].copy()

    # Clean and prepare data
    start_rec = clean_dataframe_columns(start_rec)

    # Combine two header rows
    top_row_label = top_row[:3] + second_row
    start_rec.columns = top_row_label
    start_rec = convert_currency_columns_to_numeric(start_rec)

    # Database operations
    engine = create_db_engine()
    inst_names = start_rec['Institution'].unique().tolist()
    inst_lookup = get_or_create_institutions(inst_names, engine)

    # Insert funding source data
    year = int(get_key_from_value(year_id))
    insert_funding_source_data(start_rec, inst_lookup, year, engine)

    engine.dispose()
    print(f"Table 22 processing complete\n")


def process_table_23(year_lookup):
    """
    Process Table 23: Higher education R&D expenditures by R&D field.

    Args:
        year_lookup (int): Year to process (e.g., 2021)
    """
    print(f"\n{'='*80}")
    print(f"Processing Table 23 for year {year_lookup}")
    print(f"{'='*80}\n")

    # Get year ID and build URL
    year_id = get_year_id(year_lookup)
    url = build_table_url(year_id, 23)

    # Download and parse Excel file
    df = download_excel_from_url(url)
    header_idx, title, rows_as_lists = parse_excel_headers(df, ["rank", "institution"], max_rows=5)

    # Extract header and data
    top_row = rows_as_lists[header_idx]
    start_rec = df.iloc[(header_idx + 1):].copy()

    # Clean and prepare data
    start_rec = clean_dataframe_columns(start_rec)
    start_rec.columns = top_row
    start_rec = convert_currency_columns_to_numeric(start_rec)

    # Database operations
    engine = create_db_engine()
    inst_names = start_rec['Institution'].unique().tolist()
    inst_lookup = get_or_create_institutions(inst_names, engine)

    # Insert funding field data
    year = int(get_key_from_value(year_id))
    insert_funding_field_data(start_rec, inst_lookup, year, engine)

    engine.dispose()
    print(f"Table 23 processing complete\n")


def process_table_79(year_lookup):
    """
    Process Table 79: Headcount and FTEs of R&D personnel.

    Args:
        year_lookup (str): Year to process (e.g., '2023')
    """
    print(f"\n{'='*80}")
    print(f"Processing Table 79 for year {year_lookup}")
    print(f"{'='*80}\n")

    # Get year ID and build URL
    year_id = get_year_id(year_lookup)
    url = build_table_url(year_id, 79)


    # Build URL and download
    df = download_excel_from_url(url)

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
    if year_lookup==2022:
        second_row = ['Headcount' if x == 'Personnel' else x for x in second_row]

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

    # Database connection
    engine = create_db_engine()
    conn = engine.connect()

    # Update headcount categories
    col_x = top_row[1:]
    check_cat = update_headcount_cat(col_x, engine)
    if check_cat == 1:
        print("New headcount category added to herd_headcount_cat table")
    else:
        print("No new headcount category found")

    # Link categories to field names
    headcount_counter = 0
    fte_counter = 0
    for idx in range(len(second_row)):
        if second_row[idx] == "Headcount":
            cat_check_qry = text(f"SELECT headcount_cat_id FROM herd_headcount_cat WHERE headcount_cat = '{col_x[headcount_counter]}'")
            cat_id_found = pd.read_sql_query(cat_check_qry, con=engine)
            cat_id_found = cat_id_found['headcount_cat_id'][0]
            second_row[idx] = f"{second_row[idx]}_{cat_id_found}"
            headcount_counter += 1
        elif second_row[idx] == "FTEs":
            cat_check_qry = text(f"SELECT headcount_cat_id FROM herd_headcount_cat WHERE headcount_cat = '{col_x[fte_counter]}'")
            cat_id_found = pd.read_sql_query(cat_check_qry, con=engine)
            cat_id_found = cat_id_found['headcount_cat_id'][0]
            second_row[idx] = f"{second_row[idx]}_{cat_id_found}"
            fte_counter += 1

    # Assign headers
    start_rec.columns = ["Item"] + second_row

    # Convert numeric columns
    for j in range(1, start_rec.shape[1]):
        start_rec.iloc[:, j] = (
            start_rec.iloc[:, j]
            .astype(str)
            .str.replace(r'[^0-9]', '', regex=True)
            .replace('', np.nan)
            .apply(pd.to_numeric, errors='coerce')
        )

    # Get institutions and states
    inst_names = start_rec['Item'].unique().tolist()
    inst_lookup = get_or_create_institutions(inst_names, engine)

    # Get state lookup
    check_state_qry = text("SELECT state_id, state_name FROM herd_state")
    state_lookup = pd.read_sql_query(check_state_qry, con=engine)

    # Insert headcount data
    year = int(get_key_from_value(year_id))
    insert_headcount_data(start_rec, inst_lookup, state_lookup, year, engine)

    conn.close()
    engine.dispose()
    print(f"Table 79 processing complete\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function to process all HERD tables.
    Modify the year parameters as needed for your data update cycle.
    """
    print("="*80)
    print("HERD Data Processing Pipeline")
    print("="*80)

    try:
        # Process Table 21: R&D Expenditures
        process_table_21(year_lookup=2023)

        # Process Table 22: Funding by Source
        process_table_22(year_lookup=2023)

        # Process Table 23: Funding by Field
        process_table_23(year_lookup=2023)

        # Process Table 79: Headcount and FTEs
        process_table_79(year_lookup=2023)

        print("\n" + "="*80)
        print("All tables processed successfully!")
        print("="*80)

    except Exception as e:
        print(f"\nError during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()