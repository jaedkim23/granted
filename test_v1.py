import pandas as pd
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
import requests
import datetime
from common_func import *
import difflib
from sqlalchemy import create_engine, text

api = '1228ec5f8a29051d5dd8a7fbbd01a114d6de7ef1'

host=''
user=''
password=''
port = 
schema = ''
engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{schema}"
engine = create_engine(engine_url, echo = False)
con = engine.connect()

qry  = "SELECT * FROM emp_cas"
CAS = pd.read_sql(qry, con)

search_words = ['Professor', 'Assistant Professor', 'Associate Professor', 'Lecturer']
pattern = '|'.join(search_words)
emp = CAS[CAS['position'].str.contains(pattern, case=False, na=False)]

qry  = "SELECT * FROM id_lookup"
id_lookup = pd.read_sql(qry, con)

############################################################################################################
### All CAS faculty
############################################################################################################
import clarivate.wos_starter.client
from clarivate.wos_starter.client.rest import ApiException

configuration = clarivate.wos_starter.client.Configuration(
    host = "https://api.clarivate.com/apis/wos-starter/v1"
)
configuration.api_key['ClarivateApiKeyAuth'] = api
api_inst= clarivate.wos_starter.client.DocumentsApi(clarivate.wos_starter.client.ApiClient(configuration))
current_year = datetime.datetime.now().year


#########
## test to retrieve records
# WOS
n = 0
author = emp.iloc[n]
year_select = 2000
author_wos = find_lookup_record(author['preferred_name'],emp, id_lookup)
author_wos = author_wos['wos_id'].to_list()
if len(author_wos)==0:
    df_wos = pd.DataFrame({'Number of records':[0]})
elif None not in author_wos:
    df_wos = create_record_tbl(author_wos, api_inst)
    df_wos = df_wos[df_wos['publishYear']>=year_select]
else:
    df_wos = pd.DataFrame({'Number of records':[0]})
df_wos

# Open Alex
author_alex = find_lookup_record(author['preferred_name'],emp, id_lookup)
if len(author_alex['alex_id'])==0:
    author_alex = None
elif len(author_alex['alex_id'])>1:
    author_alex = author_alex['alex_id']
    author_alex = author_alex.iloc[0]
else:
    author_alex = author_alex['alex_id'].item()

if author_alex != None:
    df_alex = create_record_tbl_alex(author_alex)
    df_alex = df_alex[df_alex['work_publication_year']>=year_select]
else: 
    df_alex = pd.DataFrame({'Number of records':[0]})

df_alex