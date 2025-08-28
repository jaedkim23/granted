import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import datetime as datetime
import re
from CAS_func_July2025 import *
import clarivate.wos_starter.client
from clarivate.wos_starter.client.rest import ApiException

load_dotenv()  # Loads variables from .env into environment

db_host = os.getenv('HOST')
db_name = os.getenv('DATABASE')
db_user = os.getenv('USERNAME')
db_password = os.getenv('PASSWORD')
db_port = os.getenv('PORT', 3306)  # Default to 3306 if not set
api = os.getenv('OUR_API')
db_user = 'admin'
engine_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(engine_url, echo=False)
con = engine.connect()

qry  = """
        SELECT E.res_id, emp_id, banner_id, first_name, middle_name, last_name, preferred_name, email, position, department, college, has_tenure 
        FROM emp_tbl E INNER JOIN fac_tbl F ON E.res_id = F.res_id
        """  
emp = pd.read_sql(qry, con)

id_lookup = pd.read_sql("SELECT * FROM id_lookup", con)

for rec in range(40,len(id_lookup)):
    id_rec = id_lookup.iloc[rec]
    res_ids = id_rec['res_id']
    open_id_lookup = "None" if id_rec['alex_id'] is None else id_rec['alex_id']
    if open_id_lookup != "None":
        X = create_record_tbl_alex(open_id_lookup)
        if not X.empty:
            for work in X.itertuples():
                work_id = work.work_id
                # Extract everything after the last "/"
                work_id = re.search(r'/([^/]*)$', work_id).group(1) if re.search(r'/([^/]*)$', work_id) else work_id    
                title = work.work_title
                title = title.replace('"', "'")  # Replace double quotes with single quotes
                publish_year = work.work_publication_year
                source = work.work_source
                # Check if the record already exists
                check_qry = """
                            SELECT open_alex_rec_id FROM open_alex_tbl WHERE res_id = "{}" AND work_id = "{}"
                            AND publish_year = {}
                            """.format(res_ids, work_id,publish_year)
                record = pd.read_sql(check_qry, con)

                if record.empty:
                    new_record = pd.DataFrame({
                    'res_id': [res_ids],
                    'work_id': [work_id],
                    'title': [title],
                    'source': [source],
                    'publish_year': [publish_year]
                    })
                    new_record.to_sql('open_alex_tbl', engine, if_exists='append', index=False)

