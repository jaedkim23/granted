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

def get_year_id(year_in):
    year_id_lookup = {'2023': 25314, '2022': 24308, '2021': 23304}
    try:
        result = year_id_lookup[str(year_in)]
    except KeyError:
        result = "Key not found"
    return result


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

def get_key_from_value(val):
    """
    Returns the first key in dictionary 'd' that has the value 'val'.
    Raises ValueError if the value is not found.
    """
    d = {'2023': 25314, '2022': 24308, '2021': 23304}
    for key, value in d.items():
        if value == val:
            return key
    raise ValueError(f"Value '{val}' not found in the dictionary.")

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