from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
import pandas as pd
import numpy as np
import os

db_host = os.getenv('HOST')
db_name = os.getenv('DATABASE')
db_user = os.getenv('USERNAME')
db_password = os.getenv('PASSWORD')
db_port = os.getenv('PORT', 3306)  # Default to 3306 if not set
db_user = 'admin'

conn = mysql.connector.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)

cursor = conn.cursor()

"""
This script updates SMSE full-time (FT) faculty. 
The raw personnel data for SMSE is unique - FT employees do not have a department or college by default. 
"""

smse_ft = pd.read_csv('Data/SMSE_FT_Faculty.csv')
### lower case all column names
smse_ft.columns = smse_ft.columns.str.lower()

for _, row in smse_ft.iterrows():
    qry = """
        INSERT IGNORE INTO smse_ft 
        (emp_id, banner_id, first_name, middle_name, last_name, position, department) 
        VALUES (%s, %s, %s, %s, %s, %s, %s) 
    """
    record = (row['employee_id'], row['banner_id'], row['firstname'], row['middle_name'], 
              row['lastname'], row['position'], row['department'])
            # Check if any value is None
    if any(pd.isna(x) for x in record):
        record = tuple(None if pd.isna(x) else x for x in record)

    cursor.execute(qry, record)

conn.commit()

