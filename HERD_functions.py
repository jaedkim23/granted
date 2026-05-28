import pandas as pd
import openpyxl
from datetime import datetime
import re
import requests
import pandas as pd
import numpy as np
import difflib
from io import BytesIO
from sqlalchemy import create_engine, text, bindparam
import sys

# NSF data URL templates
TABX_DIR1 = "https://ncses.nsf.gov/pubs/nsf"
TABX_DIR2 = "/assets/data-tables/tables/nsf"

def get_year_id(year_in):
    year_id_lookup = {'2024':26304, '2023': 25314, '2022': 24308, '2021': 23304, '2020':22311, '2019':21314}
    try:
        result = year_id_lookup[str(year_in)]
    except KeyError:
        result = "Key not found"
    return result

def get_key_from_value(val):
    """
    Returns the first key in dictionary 'd' that has the value 'val'.
    Raises ValueError if the value is not found.
    """
    d = {'2024':26304, '2023': 25314, '2022': 24308, '2021': 23304, '2020':22311, '2019':21314}
    for key, value in d.items():
        if value == val:
            return key
    return "Value not found"
    # raise ValueError(f"Value '{val}' not found in the dictionary.")

def find_best_header(df_preview):
    """
    Analyzes a preview DataFrame to find the row index with the most non-null values.
    This is likely the header row.
    """
    # Calculate the number of non-null values for each of the first 20 rows
    non_null_counts = df_preview.notna().sum(axis=1)
    
    # The best header is the one with the maximum non-null values
    best_header_index = non_null_counts.idxmax()
    
    return best_header_index


def look_up_institution(inst_list, engine_in):
    """
    Checks whether the institution already exists in table
    Input: 
        inst_list := list of institutions by name
        con_spec := connection engine to MariaDB
    Output:
        status := 0 if no instutition added, 1 if new institutions added 
    """
    # Build one named placeholder per item
    placeholders = [f":n{i}" for i in range(len(inst_list))]
    in_clause = ", ".join(placeholders)
    params = {f"n{i}": v for i, v in enumerate(inst_list)}
    check_qry = text(f"SELECT inst_id, inst_name FROM institution WHERE inst_name IN ({in_clause})")
    inst_lookup = pd.read_sql_query(check_qry, con=engine_in, params=params)

    # normalize by lower/strip
    norm_inst = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_list]
    norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in inst_lookup['inst_name']]  

    missing_inst = [orig for orig, norm in zip(inst_list, norm_inst) if norm not in set(norm_db)]

    conn = engine_in.connect()

    status = 0

    if len(missing_inst) != 0:    
        for i in range(len(missing_inst)):
            qry = text("INSERT INTO institution (inst_name, last_update) VALUES (:inst_name, :today_date)")
            record_to_insert = {"inst_name": missing_inst[i], "today_date": datetime.now()}
            conn.execute(qry, record_to_insert)
        conn.commit()
        status = 1

    return status


def check_superscript_duplicates_single_list(names_list):
    """
    Check self duplication
    """
    unique_list=[]
    to_remove=[]
    dups={} 
    names_list_copy=names_list.copy()
    for i, n in enumerate(names_list):
        for j, m in enumerate(names_list):
            if i != j:                    
                if n[:-1] == m:
                    if m not in unique_list:
                        unique_list.append(m)
                    to_remove.append(n)
                    to_remove.append(m)

                    if n not in dups.get(m,[]):
                        dups.setdefault(m, []).append(n)

                elif m[:-1] == n:
                    if n not in unique_list:
                        unique_list.append(n)

                    to_remove.append(n)
                    to_remove.append(m)

                    if m not in dups.get(n, []):
                        dups.setdefault(n, []).append(m)
                    
                elif n[:-1] == m[:-1]:
                    if n[:-1] not in unique_list:
                        unique_list.append(n[:-1])
                    to_remove.append(n)
                    to_remove.append(m)

                    if m not in dups.get(n[:-1], []):
                        dups.setdefault(n[:-1], []).append(m)
                    if n not in dups.get(n[:-1], []):
                        dups.setdefault(n[:-1], []).append(n)

    names_list_copy = [x for x in names_list_copy if x not in to_remove]

    return unique_list+names_list_copy, dups

def remove_superscript_duplicates_two_lists(old, new):
    """
    merge two lists and remove duplicates with superscripts
    """
    new_2 = [x for x in new if x not in old]
    merged = old + new_2
    return check_superscript_duplicates_single_list(merged)



def update_fund_source_cat(sources_in, con_spec):
    """
    Updates the fund_source_cat table with new sources if they do not already exist.
    Input: 
        fields_in := list of fund sources by name
        con_spec := connection engine to MariaDB
    Output:
        status := 0 if no fund fields added, 1 if new fund fields added
    """
    # Build one named placeholder per item
    if "institution" in [str(x).lower() for x in sources_in]:
        sources_in = [x for x in sources_in if not (isinstance(x, str) and x.lower() == "institution".lower())]
    placeholders = [f":n{i}" for i in range(len(sources_in))]
    in_clause = ", ".join(placeholders)
    params = {f"n{i}": v for i, v in enumerate(sources_in)}
    check_qry = text(f"SELECT fund_source_id, fund_source FROM herd_fund_source_cat WHERE fund_source IN ({in_clause})")
    sources_lookup = pd.read_sql_query(check_qry, con=con_spec, params=params)
    
    # normalize by lower/strip
    norm_sources = [re.sub(r'\s+', ' ', s).strip().lower() for s in sources_in]
    norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in sources_lookup['fund_source']]

    # Find missing sources
    missing_sources = [orig for orig, norm in zip(sources_in, norm_sources) if norm not in set(norm_db)]

    conn = con_spec.connect()
    status = 0
    if len(missing_sources) != 0:    
        for i in range(len(missing_sources)):
            qry = text("INSERT INTO herd_fund_source_cat (fund_source, last_update) VALUES (:fund_source_name, :today_date)")
            record_to_insert = {"fund_source_name": missing_sources[i], "today_date": datetime.now()}
            conn.execute(qry, record_to_insert)
        conn.commit()
        status = 1

    return status

def update_fund_field(fields_in, con_spec):
    """
    Updates the fund_field table with new fields if they do not already exist.
    Input: 
        fields_in := list of fund fields by name
        con_spec := connection engine to MariaDB
    Output:
        status := 0 if no fund fields added, 1 if new fund fields added
    """
    # Build one named placeholder per item
    placeholders = [f":n{i}" for i in range(len(fields_in))]
    in_clause = ", ".join(placeholders)
    params = {f"n{i}": v for i, v in enumerate(fields_in)}
    check_qry = text(f"SELECT field_id, field_name FROM herd_field WHERE field_name IN ({in_clause})")
    field_lookup = pd.read_sql_query(check_qry, con=con_spec, params=params)
    
    # normalize by lower/strip
    norm_fields = [re.sub(r'\s+', ' ', s).strip().lower() for s in fields_in]
    norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in field_lookup['field_name']]

    # Find missing fields
    missing_fields = [orig for orig, norm in zip(fields_in, norm_fields) if norm not in set(norm_db)]

    conn = con_spec.connect()
    status = 0
    if len(missing_fields) != 0:    
        for i in range(len(missing_fields)):
            qry = text("INSERT INTO herd_field (field_name, last_update) VALUES (:fund_field_name, :today_date)")
            record_to_insert = {"fund_field_name": missing_fields[i], "today_date": datetime.now()}
            conn.execute(qry, record_to_insert)
        conn.commit()
        status = 1

    return status


def update_state_tbl(state_in, con_spec):
    """
    Updates the herd_state table with new state if they do not already exist.
    "State" can be state or instititutional control entities
    Input: 
        state_in := list of states/institutional control by name
        con_spec := connection engine to MariaDB
    Output:
        status := 0 if no fund fields added, 1 if new fund fields added
    """
    # Build one named placeholder per item
    placeholders = [f":n{i}" for i in range(len(state_in))]
    in_clause = ", ".join(placeholders)
    params = {f"n{i}": v for i, v in enumerate(state_in)}
    check_qry = text(f"SELECT state_id, state_name FROM herd_state WHERE state_name IN ({in_clause})")
    state_lookup = pd.read_sql_query(check_qry, con=con_spec, params=params)
    
    # normalize by lower/strip
    norm_fields = [re.sub(r'\s+', ' ', s).strip().lower() for s in state_in]
    norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in state_lookup['state_name']]

    # Find missing fields
    missing_fields = [orig for orig, norm in zip(state_in, norm_fields) if norm not in set(norm_db)]

    conn = con_spec.connect()
    status = 0
    if len(missing_fields) != 0:    
        for i in range(len(missing_fields)):
            qry = text("INSERT INTO herd_state (state_name, last_update) VALUES (:state_name_val, :today_date)")
            record_to_insert = {"state_name_val": missing_fields[i], "today_date": datetime.now()}
            conn.execute(qry, record_to_insert)
        conn.commit()
        status = 1

    return status



def update_headcount_cat(cat_in, con_spec):
    """
    Updates the herd_headcount_cat table with new categories if they do not already exist.
    Input: 
        cat_in := list of headcount categories by name
        con_spec := connection engine to MariaDB
    Output:
        status := 0 if no fund fields added, 1 if new fund fields added
    """
    # Build one named placeholder per item
    placeholders = [f":n{i}" for i in range(len(cat_in))]
    in_clause = ", ".join(placeholders)
    params = {f"n{i}": v for i, v in enumerate(cat_in)}
    check_qry = text(f"SELECT headcount_cat_id, headcount_cat FROM herd_headcount_cat WHERE headcount_cat IN ({in_clause})")
    cat_lookup = pd.read_sql_query(check_qry, con=con_spec, params=params)
    
    # normalize by lower/strip
    norm_fields = [re.sub(r'\s+', ' ', s).strip().lower() for s in cat_in]
    norm_db = [re.sub(r'\s+', ' ', s).strip().lower() for s in cat_lookup['headcount_cat']]

    # Find missing fields
    missing_cat = [orig for orig, norm in zip(cat_in, norm_fields) if norm not in set(norm_db)]

    conn = con_spec.connect()
    status = 0
    if len(missing_cat) != 0:    
        for i in range(len(missing_cat)):
            qry = text("INSERT INTO herd_headcount_cat (headcount_cat, last_update) VALUES (:cat_name, :today_date)")
            record_to_insert = {"cat_name": missing_cat[i], "today_date": datetime.now()}
            conn.execute(qry, record_to_insert)
        conn.commit()
        status = 1

    return status

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

def get_actual_table_number(year, logical_table_number, engine):
    """
    Look up the actual NSF table number for a logical HERD table number.

    Args:
        year: Survey year, such as 2024
        logical_table_number: The table number expected by the processing logic,
                              such as 21, 22, 23, or 79
        engine: SQLAlchemy database engine

    Returns:
        int: Actual NSF table number for that year

    Raises:
        ValueError: If no lookup row exists for that year/table combination
    """
    query = text("""
        SELECT actual_table_number, confidence
        FROM herd_table_lookup
        WHERE year = :year
          AND logical_table_number = :logical_table_number
    """)

    result = pd.read_sql_query(
        query,
        con=engine,
        params={
            "year": int(year),
            "logical_table_number": int(logical_table_number)
        }
    )

    if result.empty:
        raise ValueError(
            f"No actual table number found for logical table "
            f"{logical_table_number} in year {year}. "
            f"Run HERD_table_number_scraper.py first."
        )

    confidence = float(result.iloc[0]["confidence"])

    if confidence < 0.75:
        print(
            f"Warning: low-confidence table match for year {year}, "
            f"logical table {logical_table_number}: confidence={confidence:.2f}"
        )

    return int(result.iloc[0]["actual_table_number"])

def get_table_url_info_for_logical_table(year_lookup, logical_table_number, engine):
    year_id = get_year_id(year_lookup)
    actual_table_number = get_actual_table_number(
        year_lookup,
        logical_table_number,
        engine
    )
    url = build_table_url(year_id, actual_table_number)

    print(
        f"Year {year_lookup}, logical table {logical_table_number} "
        f"maps to actual NSF table {actual_table_number}"
    )

    return year_id, url