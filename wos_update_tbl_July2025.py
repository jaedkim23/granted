import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import datetime as datetime
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

configuration = clarivate.wos_starter.client.Configuration(
    host = "https://api.clarivate.com/apis/wos-starter/v1"
)
configuration.api_key['ClarivateApiKeyAuth'] = api
api_inst= clarivate.wos_starter.client.DocumentsApi(clarivate.wos_starter.client.ApiClient(configuration))
current_year = datetime.datetime.now().year

id_lookup = pd.read_sql("SELECT * FROM id_lookup", con)

# for rec in range(len(id_lookup)):
for rec in range(475, 500):
    id_rec = id_lookup.iloc[rec]
    res_ids = id_rec['res_id']
    wos_lookup = id_rec['wos_id']
    print(f"Processing record {rec+1}/{len(id_lookup)}: res_id={res_ids}, wos_id={wos_lookup}")
    if wos_lookup != "None" and wos_lookup is not None:
        X = create_record_tbl([wos_lookup], api_inst)
        if not X.empty:
            for work in X.itertuples():
                work_id = work.work_id
                title = work.title
                title = title.replace('"', "'")  # Replace double quotes with single quotes
                source = work.source
                publish_year = work.publishYear
                doi = work.doi
                issn = work.issn
                eissn = work.eissn
                # Check if the record already exists

                # wos_lookup = 'LHR-4633-2024'
                # doi = '10.3390/cancers13112807'
                # q = f'DO={doi}' 
                # q = f'AI={wos_lookup}' 
                # db = 'WOS' # str | Web of Science Database abbreviation * WOS - Web of Science Core collection * BIOABS - Biological Abstracts * BCI - BIOSIS Citation Index * BIOSIS - BIOSIS Previews * CCC - Current Contents Connect * DIIDW - Derwent Innovations Index * DRCI - Data Citation Index * MEDLINE - MEDLINE The U.S. National Library of Medicine® (NLM®) premier life sciences database. * ZOOREC - Zoological Records * PPRN - Preprint Citation Index * WOK - All databases  (optional) (default to 'WOS')
                # limit = 50 # int | set the limit of records on the page (1-50) (optional) (default to 10)
                # page = 1 # int | set the result page (optional) (default to 1)
                # sort_field = 'LD+D' # str | Order by field(s). Field name and order by clause separated by '+', use A for ASC and D for DESC, ex: PY+D. Multiple values are separated by comma. Supported fields:  * **LD** - Load Date * **PY** - Publication Year * **RS** - Relevance * **TC** - Times Cited  (optional)
                # modified_time_span = None # str | Defines a date range in which the results were most recently modified. Beginning and end dates must be specified in the yyyy-mm-dd format separated by '+' or ' ', e.g. 2023-01-01+2023-12-31. This parameter is not compatible with the all databases search, i.e. db=WOK is not compatible with this parameter. (optional)
                # tc_modified_time_span = None # str | Defines a date range in which times cited counts were modified. Beginning and end dates must be specified in the yyyy-mm-dd format separated by '+' or ' ', e.g. 2023-01-01+2023-12-31. This parameter is not compatible with the all databases search, i.e. db=WOK is not compatible with this parameter. (optional)
                # detail = None # str | it will returns the full data by default, if detail=short it returns the limited data (optional)

                # api_response = api_inst.documents_get(q, db=db, limit=limit, page=page, sort_field=sort_field, modified_time_span=modified_time_span, tc_modified_time_span=tc_modified_time_span, detail=detail)
                # zz = api_response.to_dict()
                # zz.keys()
                # zz['hits']
                # zz['metadata']['total']
                # get_wos_data_ai_og


                check_qry = """
                            SELECT wos_rec_id FROM wos_tbl WHERE work_id = "{}"
                            AND publish_year = {} AND doi = "{}"
                            AND issn = "{}" AND eissn = "{}"
                            """.format(work_id,publish_year, doi, issn, eissn)
                record = pd.read_sql(check_qry, con)

                if record.empty:
                    # Insert new work record
                    new_record = pd.DataFrame({
                    'work_id': [work_id],
                    'title': [title],
                    'source': [source],
                    'publish_year': [publish_year],
                    'doi': [doi],
                    'issn': [issn],
                    'eissn': [eissn]
                    })
                    new_record.to_sql('wos_tbl', engine, if_exists='append', index=False)
                    con.commit()

                # Get the wos_rec_id (whether record was just inserted or already existed)
                check_qry_wos = """
                                SELECT wos_rec_id FROM wos_tbl WHERE work_id = '{}'
                                """.format(work_id)
                wos_result = pd.read_sql(check_qry_wos, con)
                
                wos_rec_id = wos_result.iloc[0]['wos_rec_id']
                    
                # Insert the relationship record
                relationship_record = pd.DataFrame({
                    'wos_rec_id': [wos_rec_id],
                    'res_id': [res_ids]
                })
                relationship_record.to_sql('wos_work_tbl', engine, if_exists='append', index=False)
                con.commit()
