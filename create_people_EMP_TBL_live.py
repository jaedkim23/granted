import os
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
import pandas as pd
import numpy as np
import time
import json
import requests
import re
import random
import datetime
import difflib

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
This script processes the CSV file 'USD_Active_Employees_Publications_Research_Report.csv' to extract information about employees.
Information is inserted into multiple tables in the database, specifically into the 'emp_tbl' table (and associated fac_tbl and nonfac_tbl tables) and the 'emp_cas' table.
"""

df = pd.read_csv('USD_Active_Employees_Publications_Research_Report.csv')
### lower case all column names
df.columns = df.columns.str.lower()
### Remove "Pxxxx" in the position column
df['position'] = df['position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')
df['position'] = df['position'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
df['position'] = df['position'].str.replace(')', '', regex=False).str.strip()
df['position'] = df['position'].str.replace(r'\d+$', '', regex=True).str.strip()

# Find all values in the position column that contain "professor" or "lecturer" (case-insensitive)
matches = df[df['position'].str.contains(r'professor|lecturer|faculty|dean|instructor', case=False, na=False)]
matches = matches['position'].unique()
remove_pos = ['Faculty Support Specialist','Faculty Assistant','Assistant to the Dean/Fiscal Affair','Executive Assistant to the Dean',
              'Campus Recreation Instructor - Temporary','Campus Recreation Instructor','Campus Rec Instructor','Summer Instructor',
              'Visiting Professor','Supervisor, Law School Faculty Support', 'Student - GA Teaching-LSM Lecturer I',
              'Recreation Swim Instructor','Madrid Visiting Faculty','Campus Rec Instructor',
              'Visiting Assistant Professor','Graphic Design','Lifeguard & Swim Instructor', 'Faculty Services Librarian',
              'Executive Assistant to the Dean of the School of Law','Copley Library - Faculty Research Student Intern',
              'Student - Recreation Instructor','Student Instructor','Faculty IT Support Specialist',
              'Assistant Dean of Student Engagement and Inclusive Excellence',
              'Supply Chain Industry Outreach Professional','Student Professional Development Manager','Senior Director of Student Professional Development',
              'Professional Development Manager','Student and Career Services Professional','Senior Coordinator of Student Professional Development',
              'Professional - Academics','Professional','Professional - Finance Instruction CCUSA','Clerical Worker - Professional','Professional - Academics - Temporary',
              'Clerical Worker - Professional', 'Professional', 'Professional - Academics - CLA Coach', 'Professional - NPI - Temporary', 'The Nonprofit Institute Graduate Assistant',
              'The Nonprofit Institute Fellow','Professional - Academics - Temporary',
              'Coordinator, Strategic Initiatives and Deans Office',
              'Assistant to the Dean/Fiscal Affairs','Executive Assistant II to the Dean',
              'Professional Academics', 'Professional Academics -', 'Professional Academics - Course Development','Professional Academic',
              'Director of Professional and Public Programs','Graduate Assistant Lecturer I','Program Manager, Professional and Public Programs','Professional - Student Services - Temporary',
              'Associate Dean of Student Success and Diversity'
              ]
matches = [match for match in matches if match not in remove_pos]

### Determine which supervisory organization the employee belongs to
for emp in range(len(df)):
    rec = df.iloc[emp]
    emp_id = int(rec['employee_id']) if (rec['employee_id']!=None) else None
    banner_id = int(rec['banner_id']) if (rec['banner_id']!=None) else None
    author_first = rec['firstname'] if (rec['firstname']!=None) else None
    author_middle = rec['middle_name'] if (rec['middle_name']!=None) else None
    author_last = rec['lastname'] if (rec['lastname']!=None) else None
    author_preferred = rec['preferred_name'] if (rec['preferred_name']!=None) else None
    author_email = rec['primaryworkemail'] if (rec['primaryworkemail']!=None) else None
    author_phone = rec['primaryworkphone'] if (rec['primaryworkphone']!=None) else None
    has_tenure = int(rec['has_tenure']) if (rec['has_tenure']!=None) else None
    
    pos = rec['position'] if (rec['position']!=None) else None
    ### Checks if employee is a faculty member
    is_fac = (True if pos in matches else False) or (True if rec['has_tenure']==1 else False)
    
    ### for CAS, we need to check if the college is 'College of Arts and Sciences'
    if rec['college'] == 'College of Arts and Sciences':
        college_short = 'CAS'
        # Extract department or unit within CAS
        rec['supervisory_organization'] = re.sub(r'\(.*?\)', '', str(rec['supervisory_organization'])).strip()      
        # Remove extra parenthesis in Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', rec['supervisory_organization']).strip()
        # Remove 'College of Arts and Sciences -' from the Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'^College of Arts and Sciences -\s*', '', str(rec['supervisory_organization'])).strip()
        # Remove numbers and extra close parenthesis at the end of Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove any numbers at the end of Supervisory_Organization and Department, and Position
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None

        college = rec['college'] if (rec['college']!=None) else "College of Arts and Sciences"
        rec['department'] = re.sub(r'\(.*?\)', '', rec['department']).strip()
        
        department = rec['department'] if (rec['department']!=None) else None
    
    ### for SMSE, we need to check if the supervisory_organization is 'School of Engineering'    
    elif ('School of Engineering' in str(rec['supervisory_organization'])):
        college_short = 'SMSE'
        # Remove extra parenthesis in Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', rec['supervisory_organization']).strip()
        # Remove 'College of Engineering -' from the Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'^College of Engineering -\s*', '', str(rec['supervisory_organization'])).strip()
        # Remove numbers and extra close parenthesis at the end of Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove any numbers at the end of Supervisory_Organization and Department, and Position
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None

        college = "School of Engineering" if pd.isna(rec['college']) else rec['college']

        if pd.isna(rec['department']):
            ### Find department from other table
            check_smse_qry = """SELECT department FROM smse_ft WHERE EMP_ID = %s"""
            cursor.execute(check_smse_qry, (emp_id,))
            dept = cursor.fetchall()
            rec['department'] = dept[0][0] if dept else "School of Engineering"

        # Remove description in parenthesis in Department
        rec['department'] = re.sub(r'\s*\(.*?\)', '', rec['department']).strip()
        # Remove extra parenthesis in Department
        rec['department'] = re.sub(r'\)', '', rec['department']).strip()

        # Remove any numbers at the end of Supervisory_Organization and Department, and Position
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        rec['department'] = re.sub(r'\d+$', '', rec['department']).strip()
        
        department = rec['department'] if (rec['department']!=None) else None

    ### for SOLES, we need to check if the college is 'School of Leadership and Education XXX'
    elif ('School of Leadership and Education' in str(rec['college'])):
        college_short = 'SOLES'
        # Extract department or unit within SOLES
        # Remove description in parenthesis in College column
        rec['college'] = re.sub(r'\s*\(.*?\)', '', str(rec['college'])).strip()
        # Remove extra parenthesis in College column
        rec['college'] = re.sub(r'\)', '', rec['college']).strip()
        # Remove description in parenthesis in College column with open "("
        rec['college'] = re.sub(r'\s*\(.*', '', rec['college']).strip()
        # Replace "School of Leadership and Education Science" with "School of Leadership and Education Sciences"
        rec['college'] = re.sub(r'\bSchool of Leadership and Education Science\b', 'School of Leadership and Education Sciences', rec['college'])

        # Extract department or unit within SOLES
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', str(rec['supervisory_organization'])).strip()
        # Remove extra parenthesis in Supervisory_Organization column   
        rec['supervisory_organization'] = re.sub(r'\)','', rec['supervisory_organization']).strip()
        rec['supervisory_organization'] = re.sub(r'^School of Leadership and Education Sciences -\s*', '', str(rec['supervisory_organization'])).strip()

        ### Special case: "Smith)" in department - remove
        rec['department'] = "School of Leadership and Education Sciences" if rec['department']=="Smith)" else rec['department']

        # Remove description in parenthesis in Department
        rec['department'] = re.sub(r'\s*\(.*?\)', '', rec['department']).strip()

        # Remove extra parenthesis in Department
        rec['department'] = re.sub(r'\)', '', rec['department']).strip()

        # Remove numbers at the end of Supervisory_Organization and Department, and Position
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        rec['department'] = re.sub(r'\d+$', '', rec['department']).strip()

        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None

        college = "School of Leadership and Education Sciences" if pd.isna(rec['college']) else rec['college']
        department = rec['department'] if (rec['department']!=None) else None

    ### for Peace, we need to check the supervisory_organization
    elif ('School of Peace Studies' in str(rec['supervisory_organization'])):
        college_short = 'KIPJ'

        # Remove extra parenthesis in Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', rec['supervisory_organization']).strip()
        # Remove numbers and extra close parenthesis at the end of Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove 'School of Peace -' from the Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'^School of Peace Studies -\s*', '', str(rec['supervisory_organization'])).strip()
        
        # Remove description in parenthesis in Department
        rec['department'] = "School of Peace Studies" if pd.isna(rec['department']) else rec['department']
        rec['department'] = re.sub(r'\s*\(.*?\)', '', rec['department']).strip()
        # Remove extra parenthesis in Department
        rec['department'] = re.sub(r'\)', '', rec['department']).strip()

        # Remove any numbers at the end of Supervisory_Organization and Department, and Position
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None
        
        department = "School of Peace Studies" if pd.isna(rec['department']) else rec['department']
        college = "School of Peace Studies" if pd.isna(rec['college']) else rec['college']

    elif ('School of Nursing and Health Science' in str(rec['supervisory_organization'])):
        college_short = 'HSN'
        # Remove extra parenthesis in Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', rec['supervisory_organization']).strip()
        # Remove numbers and extra close parenthesis at the end of Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove 'School of Nursing and Health Science -' from the Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'^School of Nursing and Health Science -\s*', '', str(rec['supervisory_organization'])).strip()

        # Remove description in parenthesis in Department
        rec['department'] = "School of Nursing and Health Science" if pd.isna(rec['department']) else rec['department']
        rec['department'] = re.sub(r'\s*\(.*?\)', '', rec['department']).strip()
        # Remove extra parenthesis in Department
        rec['department'] = re.sub(r'\)', '', rec['department']).strip()
        rec['department'] = re.sub(r'\d+$', '', rec['department']).strip()
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None
        
        department = "School of Nursing and Health Science" if pd.isna(rec['department']) else rec['department']
        college = "School of Nursing and Health Science" if pd.isna(rec['college']) else rec['college']

    elif ('Professional and Continuing Education' in str(rec['college'])):
        college_short = 'PCE'

        # Remove extra parenthesis in Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', rec['supervisory_organization']).strip()
        # Remove numbers and extra close parenthesis at the end of Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove 'Professional and Continuing Education -' from the Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'^Professional and Continuing Education -\s*', '', str(rec['supervisory_organization'])).strip()

        # Remove description in parenthesis in Department        
        rec['department'] = "Professional and Continuing Education" if pd.isna(rec['department']) else rec['department']
        rec['department'] = re.sub(r'\s*\(.*?\)', '', rec['department']).strip()
        # Remove extra parenthesis in Department
        rec['department'] = re.sub(r'\)', '', rec['department']).strip()
        rec['department'] = re.sub(r'\d+$', '', rec['department']).strip()
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None

        department = "Professional and Continuing Education" if pd.isna(rec['department']) else rec['department']
        college = "Professional and Continuing Education" if pd.isna(rec['college']) else rec['college']

    elif ('Copley Library' in str(rec['supervisory_organization'])):
        college_short = 'Copley'

        # Remove extra parenthesis in Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', rec['supervisory_organization']).strip()
        # Remove numbers and extra close parenthesis at the end of Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove 'Copley Library -' from the Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'^Copley Library -\s*', '', str(rec['supervisory_organization'])).strip()

        # Remove description in parenthesis in Department
        rec['department'] = "Copley Library" if pd.isna(rec['department']) else rec['department']
        rec['department'] = re.sub(r'\s*\(.*?\)', '', rec['department']).strip()
        # Remove extra parenthesis in Department
        rec['department'] = re.sub(r'\)', '', rec['department']).strip()
        rec['department'] = re.sub(r'\d+$', '', rec['department']).strip()
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None

        department = "Copley Library" if pd.isna(rec['department']) else rec['department']
        college = "Copley Library" if pd.isna(rec['college']) else rec['college']

    else:
        college_short = 'Other'

        # Remove extra parenthesis in Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', rec['supervisory_organization']).strip()
        # Remove numbers and extra close parenthesis at the end of Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove 'Copley Library -' from the Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'^Copley Library -\s*', '', str(rec['supervisory_organization'])).strip()

        # Remove description in parenthesis in Department
        rec['department'] = "Other" if pd.isna(rec['department']) else rec['department']
        rec['department'] = re.sub(r'\s*\(.*?\)', '', rec['department']).strip()
        # Remove extra parenthesis in Department
        rec['department'] = re.sub(r'\)', '', rec['department']).strip()
        rec['department'] = re.sub(r'\d+$', '', rec['department']).strip()
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None

        department = "Other" if pd.isna(rec['department']) else rec['department']
        college = "Other" if pd.isna(rec['college']) else rec['college']

    qry =   """
                INSERT INTO emp_tbl 
                (EMP_ID, BANNER_ID, FIRST_NAME, MIDDLE_NAME, LAST_NAME, PREFERRED_NAME, EMAIL, WORK_PHONE) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
    record = (emp_id, banner_id, author_first, author_middle, author_last, author_preferred, author_email, author_phone)

    # Check if any value is None
    if any(pd.isna(x) for x in record):
        record = tuple(None if pd.isna(x) else x for x in record)

    cursor.execute(qry, record)
    conn.commit()

    if is_fac:
        insert_qry_fac_tbl = """
        INSERT INTO fac_tbl
        (RES_ID, POSITION, DEPARTMENT, COLLEGE, HAS_TENURE)
        VALUES (%s, %s, %s, %s, %s)
        """
        get_res_id_qry = """SELECT RES_ID FROM emp_tbl WHERE BANNER_ID = %s"""
        cursor.execute(get_res_id_qry, (banner_id,))
        res_id = cursor.fetchall()
        if len(res_id)>0:
            res_id = res_id[0][0]
            insert_rec = (res_id, pos, department, college, has_tenure)
            cursor.execute(insert_qry_fac_tbl, insert_rec)
            conn.commit()
    else:
        insert_qry_nonfac_tbl = """
        INSERT INTO nonfac_tbl
        (RES_ID, POSITION, SUPERVISORY_ORG, COLLEGE)
        VALUES (%s, %s, %s, %s)
        """
        get_res_id_qry = """SELECT res_id FROM emp_tbl WHERE BANNER_ID = %s"""
        cursor.execute(get_res_id_qry, (banner_id,))
        res_id = cursor.fetchall()
        if len(res_id)>0:
            res_id = res_id[0][0]
            insert_rec = (res_id, pos, sup_org, college)
            cursor.execute(insert_qry_nonfac_tbl, insert_rec)
            conn.commit()

