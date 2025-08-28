import pandas as pd
from dotenv import load_dotenv
from mysql.connector import Error
from sqlalchemy import create_engine, text
import numpy as np
import os
load_dotenv()  # Loads variables from .env into environment

csv_url = "http://lws.sandiego.edu/department-report/get-dirs.php"
DF = pd.read_csv(csv_url, delimiter="|")

DF_out = pd.DataFrame({'BannerID': [], 'Name': [], 'Email': [], 'Unit':[]})

for rec in range(len(DF)):
    emp = DF.iloc[rec]
    emp_name = emp['Name']
    emp_email = emp['E-mail']
    emp_bannerid = emp['BannerID']
    emp_dept = emp['Department']
    emp_sub_dept = emp['SubDepartment']
    emp_subunit = emp['SubUnit']
    
    # exclude_columns = ['Name','E-mail','Department','SubDepartment','SubUnit']
    # add_columns = [col for col in DF.columns if col not in exclude_columns]

    if not pd.isna(emp_dept):
        dept_items = str(emp_dept).split(";")
        for dept in dept_items:
            dept = dept.strip()
            if dept:  # Only add non-empty strings
                DF_add = pd.DataFrame({'BannerID': [emp_bannerid], 'Name': [emp_name], 'Email': [emp_email], 'Unit': [dept]})
                DF_out = pd.concat([DF_out, DF_add], ignore_index=True)

    if not pd.isna(emp_sub_dept):
        sub_dept_items = str(emp_sub_dept).split(";")
        for sub_dept in sub_dept_items:
            sub_dept = sub_dept.strip()
            if sub_dept:  # Only add non-empty strings
                DF_add = pd.DataFrame({'BannerID': [emp_bannerid], 'Name': [emp_name], 'Email': [emp_email], 'Unit': [sub_dept]})
                DF_out = pd.concat([DF_out, DF_add], ignore_index=True)

    if not pd.isna(emp_subunit):
        emp_subunit = str(emp_subunit).split(";")
        for unit in emp_subunit:
            unit = unit.strip()
            if unit:  # Only add non-empty strings
                DF_add = pd.DataFrame({'BannerID': [emp_bannerid], 'Name': [emp_name], 'Email': [emp_email], 'Unit': [unit]})
                DF_out = pd.concat([DF_out, DF_add], ignore_index=True)

load_dotenv()  # Loads variables from .env into environment

db_host = os.getenv('HOST')
db_name = os.getenv('DATABASE')
db_user = os.getenv('USERNAME')
db_password = os.getenv('PASSWORD')
db_port = os.getenv('PORT', 3306)  # Default to 3306 if not set

engine_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(engine_url, echo=False)
con = engine.connect()

missing_emps = []
for rec in range(len(DF_out)):
    emp = DF_out.iloc[rec]
    emp_name = emp['Name']
    emp_email = emp['Email']
    emp_bannerid = emp['BannerID']
    emp_subunit = emp['Unit']
    
    qry  = "SELECT res_id, emp_id, banner_id, preferred_name FROM emp_tbl WHERE banner_id= '{}'".format(emp_bannerid)      
    emp_found = pd.read_sql(qry, con)
    if emp_found.empty:
        print(f"Banner ID {emp_bannerid} not found for {emp_name}.")
        missing_emps.append(emp_bannerid)
        continue
    else:
        res_id = emp_found['res_id'].values[0]
        preferred_name = emp_found['preferred_name'].values
        check_qry = '''SELECT * FROM EMP_ORGS WHERE res_id = {} AND banner_id= {} AND full_name = "{}" 
                        AND email = "{}" AND UNIT = "{}"'''.format(res_id, emp_bannerid, emp_name, emp_email, emp_subunit)
        check_df = pd.read_sql(check_qry, con)        
        if check_df.empty:
            insert_qry = 'INSERT INTO EMP_ORGS (res_id, banner_id, full_name, email, UNIT) VALUES ({}, "{}", "{}", "{}", "{}")'.format(res_id, emp_bannerid, emp_name, emp_email, emp_subunit)
            con.execute(text(insert_qry))
            con.commit()


check_missing = DF_out.loc[DF_out['BannerID'].isin(missing_emps)]
check_missing['Name'].unique()