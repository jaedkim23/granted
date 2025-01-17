from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine, text

#### Add your MySQL credentials
conn = mysql.connector.connect(
    host='',
    database='',
    user='',
    password=''
)

cursor = conn.cursor()

df = pd.read_csv('USD_Active_Employees_Publications_Research_Report.csv')

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

