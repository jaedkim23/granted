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
matches = df[df['position'].str.contains(r'professor|lecturer|faculty|dean|instructor|assistant prof|associate prof|prof', case=False, na=False)]
matches = matches['position'].unique()
remove_pos = ['Faculty Support Specialist','Faculty Assistant','Assistant to the Dean/Fiscal Affair',
              'Campus Recreation Instructor - Temporary','Campus Recreation Instructor',
              'Visiting Professor','Supervisor, Law School Faculty Support', 'Student - GA Teaching-LSM Lecturer I',
              'Recreation Swim Instructor','Madrid Visiting Faculty',
              'Visiting Assistant Professor','Graphic Design','Campus Recreation Instructor','Lifeguard & Swim Instructor', 'Faculty Services Librarian',
              'Executive Assistant to the Dean of the School of Law','Copley Library - Faculty Research Student Intern',
              'Student - Recreation Instructor','Student Instructor','Faculty IT Support Specialist',
              'Assistant Dean of Student Engagement and Inclusive Excellence',
              'Supply Chain Industry Outreach Professional','Student Professional Development Manager','Senior Director of Student Professional Development',
              'Professional Development Manager','Student and Career Services Professional','Senior Coordinator of Student Professional Development',
              ]
matches = [match for match in matches if match not in remove_pos]

"""
fac_list = ['Professor', 'Adjunct Instructor', 'Associate Professor', 'Lecturer II','Adjunct Assistant Professor', 'Lecturer','Lecturer I',
            'Faculty Mentor','Applied Music Instructor','Assistant Dean','Professor of Practice',
            'Assistant Professor', 'Visiting Assistant Professor', 'Visiting Professor','Adjunct Professor', 'Adjunct Assistant Professor and Director of National Scholarships',
            'Professor of Practice & Writing Center Director', 'Clare Boothe Luce Assistant Professor of Physics', 'Assistant Professor, Computer Science',
            'Assistant Prof, Indus & Systems Engineering', 'Adjunct Associate Professor',
            'Clinical Professor','Clinical Professor of Finance',
            'Clinical Professor of Management',  'Clinical Professor of Business Law and Ethics',  'Assistant Professor of Economics',  'Professor of Accounting', 'Lecturer II - DLS',
            'Co-Executive Director and Professor of Practice',       'Lecturer I - DLS Nonprofit','Lecturer II - DLT', 'Lecturer/Supervisor','Lecturer II- Online M.Ed',
            'Lecturer II - OLMED','Lecturer II - MSNP','Applied Instructor, MFT and Director of Clinical Training','Lecturer I - DLT',
            'Professor of Practice, Dir of Field Experiences','Lecturer II - EDSJ', 'Lecturer II - DLT EDSJ', 'Professor, Education for Social Justice',
            'GA Teaching-LSM Lecturer I',
            'Lecturer II - Restorative Justice', 'Lecturer II - Restorative Justice', 'DLS Graduate Assistant',
            'GA Teaching - Lecturer I',
            'Lecturer II - DLS Restorative Justice','Lecturer II- DLT EDSJ','Lecturer I - MSHA','Lecturer II - MSHA',    'Adjunct Clinical Associate Professor',
            'Lecturer/Supervisor II', 'Associate Dean, School of Nursing', 'Adjunct Clinical Professor','Lecturer I - LEPS', 'Lecturer I - CSOL', 'Lecturer - Extension Programs',
            'Lecturer I - SOLES','Lecturer II - CSOL','Lecturer - II', 'Lecturer II - LEPSL','Lecturer I - Extension Programs',
            'Lecturer I - Academic Programs', 'Lecturer I - Admin', 'Lecturer - Summer Junior Program','Lecturer - Junior Program TEACHING',
            'Professor of Practice & Writing Program Director']
"""

### Determine which supervisory organization the employee belongs to
df_test1 = pd.DataFrame({'emp_id': [], 'banner_id': [], 'first_name': [], 'middle_name': [], 'last_name': [], 'preferred_name': [], 'email': [], 'work_phone': [] })
df_test2 = pd.DataFrame({'banner_id': [], 'position': [], 'department': [], 'college': [], 'has_tenure': []})
df_test3 = pd.DataFrame({'banner_id': [], 'position': [], 'supervisory_org': [], 'college': []})

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
    is_fac = True if pos in matches else False
    
    ### for SMSE, we need to check if the supervisory_organization is 'School of Engineering'    
    if ('School of Business' in str(rec['college'])):
        college_short = 'KSB'
        # Extract department or unit within SOB
        rec['supervisory_organization'] = re.sub(r'\s*\(.*?\)', '', rec['supervisory_organization']).strip()
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove 'School of Business -' from the Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'^School of Business -\s*', '', str(rec['supervisory_organization'])).strip()
        
        # Remove description in parenthesis in Department
        rec['department'] = re.sub(r'\s*\(.*?\)', '', rec['department']).strip()
        # Remove extra parenthesis in Department
        rec['department'] = re.sub(r'\)', '', rec['department']).strip()

        # Remove any numbers at the end of Supervisory_Organization and Department, and Position
        rec['department'] = re.sub(r'\d+$', '', rec['department']).strip()
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        # Remove numbers and extra close parenthesis at the end of Supervisory_Organization
        rec['supervisory_organization'] = re.sub(r'\)', '', rec['supervisory_organization']).strip()
        # Remove any numbers at the end of Supervisory_Organization and Department, and Position
        rec['supervisory_organization'] = re.sub(r'\d+$', '', rec['supervisory_organization']).strip()
        sup_org = rec['supervisory_organization'] if (rec['supervisory_organization']!=None) else None

        college = "School of Business" if pd.isna(rec['college']) else rec['college']

        DF_add1 = pd.DataFrame({'emp_id': [emp_id], 'banner_id': [banner_id], 'first_name': [author_first], 'middle_name': [author_middle], 'last_name': [author_last], 'preferred_name': [author_preferred], 'email': [author_email], 'work_phone': [author_phone]})
        df_test1 = pd.concat([df_test1, DF_add1], ignore_index=True)

        if is_fac:
            DF_add2 = pd.DataFrame({'banner_id': [banner_id], 'position': [pos], 'department': [department], 'college': [college], 'has_tenure': [has_tenure]})
            df_test2 = pd.concat([df_test2, DF_add2], ignore_index=True)
        else:
            DF_add3 = pd.DataFrame({'banner_id': [banner_id], 'position': [pos], 'supervisory_org': [sup_org], 'college': [college]})
            df_test3 = pd.concat([df_test3, DF_add3], ignore_index=True)

df_test1.to_csv('df_test1.csv', index=False)
df_test2.to_csv('df_test2.csv', index=False)
df_test3.to_csv('df_test3.csv', index=False)





SOLES = df[df['college'].str.contains('School of Leadership and Education', na=False)]
Peace = df[df['supervisory_organization'].str.contains('School of Peace Studies', na=False)]
Nurse = df[df['supervisory_organization'].str.contains('School of Nursing and Health Science', na=False)]
PCE = df[df['college'].str.contains('Professional and Continuing Education', na=False)]
Copley = df[df['supervisory_organization'].str.contains('Copley Library', na=False)]


### Process position column

CAS['Position'] = CAS['Position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')

# Remove description in parenthesis in the Position column
CAS['Position'] = CAS['Position'].str.replace(r'\s*\(.*?\)', '', regex=True)
CAS['Position'] = CAS['Position'].str.strip()
CAS['Position'] = CAS['Position'].str.replace(r'\d+$', '', regex=True).str.strip()
SMSE['Position'] = SMSE['Position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')

# Remove description in parenthesis in the Position column

SMSE['Position'] = SMSE['Position'].str.replace(r'\s*\(.*?\)', '', regex=True)
SMSE['Position'] = SMSE['Position'].str.strip()

SMSE['Position'] = SMSE['Position'].str.replace(r'\d+$', '', regex=True).str.strip()



SOB['Position'] = SOB['Position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')

# Remove description in parenthesis in the Position column
SOB['Position'] = SOB['Position'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()

# Remove extra parenthesis in Position column
SOB['Position'] = SOB['Position'].str.replace(')', '', regex=False).str.strip()


SOB['Position'] = SOB['Position'].str.replace(r'\d+$', '', regex=True).str.strip()

SOB = SOB.dropna(subset = ['Position'])




SOLES['Position'] = SOLES['Position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')
SOLES['Position'] = SOLES['Position'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
SOLES['Position'] = SOLES['Position'].str.replace(')', '', regex=False).str.strip() 

SOLES['Position'] = SOLES['Position'].str.replace(r'\d+$', '', regex=True).str.strip()

SOLES = SOLES.dropna(subset = ['Position'])




Peace['Position'] = Peace['Position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')
Peace['Position'] = Peace['Position'].str.replace(r'\s*\(.*?\)', '', regex=True)
Peace['Position'] = Peace['Position'].str.strip()

Peace['Position'] = Peace['Position'].str.replace(r'\d+$', '', regex=True).str.strip()

Peace = Peace.dropna(subset = ['Position'])



Nurse['Position'] = Nurse['Position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')
Nurse['Position'] = Nurse['Position'].str.replace(r'\s*\(.*?\)', '', regex=True)
Nurse['Position'] = Nurse['Position'].str.strip()



Nurse['Position'] = Nurse['Position'].str.replace(r'\d+$', '', regex=True).str.strip()

Nurse = Nurse.dropna(subset = ['Position'])


PCE['Position'] = PCE['Position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')
PCE['Position'] = PCE['Position'].str.replace(r'\s*\(.*?\)', '', regex=True)
PCE['Position'] = PCE['Position'].str.strip()

PCE['Position'] = PCE['Position'].str.replace(r'\d+$', '', regex=True).str.strip()

PCE = PCE.dropna(subset = ['Position'])


Copley['Position'] = Copley['Position'].apply(lambda x: ' '.join(str(x).split()[1:]) if pd.notna(x) and len(str(x).split()) > 1 else '')
Copley['Position'] = Copley['Position'].str.replace(r'\s*\(.*?\)', '', regex=True)
Copley['Position'] = Copley['Position'].str.replace(r'\s* - Library', '', regex=True).str.strip()
Copley['Position'] = Copley['Position'].str.strip()


Copley['Position'] = Copley['Position'].str.replace(r'\d+$', '', regex=True).str.strip()

Copley = Copley.dropna(subset = ['Position'])





position = rec['position'] if (rec['position']!=None) else None
department = rec['department'] if (rec['department']!=None) else None
college = rec['college'] if (rec['college']!=None) else None



regex_pattern = r'[\(-]'
df_college = df['Supervisory_Organization'].str.split(regex_pattern).apply(lambda x: [elem for elem in x if elem])
df['College'] = df_college.apply(lambda x: x[0] if len(x) > 0 else np.nan)
df['College'] = df['College'].apply(lambda x: x.strip() if isinstance(x, str) else x)

CAS = df.copy()
CAS = CAS[CAS['College']=="College of Arts and Sciences"]
CAS['Department'] = CAS['Department'].str.split('(').str[0].str.strip()

### Optional: readout to CAS.pkl
### CAS.to_pickle('Data/CAS.pkl')

# Remove words in parentheses
CAS['Position'] = CAS['Position'].apply(lambda x: re.sub(r'\(.*?\)', '', x))
# Remove any numbers at the end of the string (e.g. 'Assistant 1', 'Assistant 2', 'Assistant 3')
CAS['Position'] = CAS['Position'].apply(lambda x: re.sub(r'\d+$', '', x))
# Remove whitespace
CAS['Position'] = CAS['Position'].apply(lambda x: x.rstrip())
# Remove first part of position
CAS['Position'] = CAS['Position'].apply(lambda x: ' '.join(x.split()[1:]) if x.split()[0].startswith('P') else x)

# Remove supervisory organization column
CAS = CAS[['Employee_ID','Banner_ID','firstName','Middle_Name','lastName','Preferred_Name','primaryWorkEmail','primaryWorkPhone','Has_Tenure','Position','Department','College']]
CAS = CAS.drop_duplicates()
CAS.columns = CAS.columns.str.lower()
CAS = CAS.where(pd.notna(CAS), None)
### Insert records into emp_cas table in DB
for n in range(len(CAS)):
    emp = CAS.iloc[n]

    qry = """
    INSERT INTO EMP_CAS 
    (EMP_ID, BANNER_ID, FIRST_NAME, MIDDLE_NAME, LAST_NAME, PREFERRED_NAME, EMAIL, WORK_PHONE, HAS_TENURE, POSITION, DEPARTMENT, COLLEGE) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    emp_id = int(emp['employee_id']) if (emp['employee_id']!=None) else None
    banner_id = int(emp['banner_id']) if (emp['banner_id']!=None) else None
    author_first = emp['firstname'] if (emp['firstname']!=None) else None
    author_middle = emp['middle_name'] if (emp['middle_name']!=None) else None
    author_last = emp['lastname'] if (emp['lastname']!=None) else None
    author_preferred = emp['preferred_name'] if (emp['preferred_name']!=None) else None
    author_email = emp['primaryworkemail'] if (emp['primaryworkemail']!=None) else None
    author_phone = emp['primaryworkphone'] if (emp['primaryworkphone']!=None) else None
    has_tenure = int(emp['has_tenure']) if (emp['has_tenure']!=None) else None
    position = emp['position'] if (emp['position']!=None) else None
    department = emp['department'] if (emp['department']!=None) else None
    college = emp['college'] if (emp['college']!=None) else None

    record = (emp_id, banner_id, author_first, author_middle, author_last, author_preferred, author_email, author_phone, has_tenure, position, department, college)
    cursor.execute(qry, record)
    conn.commit()

cursor.close()
conn.close()
