import os
import time
import json
import pandas as pd
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
from sqlalchemy import create_engine, text
import requests
import re
import random
import datetime as datetime
from CAS_func_July2025 import *
import difflib
import numpy as np

load_dotenv()  # Loads variables from .env into environment

db_host = os.getenv('HOST')
db_name = os.getenv('DATABASE')
db_user = os.getenv('USERNAME')
db_password = os.getenv('PASSWORD')
db_port = os.getenv('PORT', 3306)  # Default to 3306 if not set
db_user = 'admin'
engine_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(engine_url, echo=False)
con = engine.connect()

qry  = """
        SELECT E.res_id, emp_id, banner_id, first_name, middle_name, last_name, preferred_name, email, position, department, college, has_tenure 
        FROM emp_tbl E INNER JOIN fac_tbl F ON E.res_id = F.res_id
        """  
emp = pd.read_sql(qry, con)

############################################################################################################
### All faculty
############################################################################################################
import clarivate.wos_starter.client
from clarivate.wos_starter.client.rest import ApiException
api = '1228ec5f8a29051d5dd8a7fbbd01a114d6de7ef1'
configuration = clarivate.wos_starter.client.Configuration(
    host = "https://api.clarivate.com/apis/wos-starter/v1"
)
configuration.api_key['ClarivateApiKeyAuth'] = api
api_inst= clarivate.wos_starter.client.DocumentsApi(clarivate.wos_starter.client.ApiClient(configuration))
current_year = datetime.datetime.now().year

for n in range(0, len(emp)):
    df = pd.DataFrame(columns=['res_id', 'wos_id', 'author_name', 'search_term'])
    res_id = int(emp.iloc[n]['res_id'])
    author_last = emp.iloc[n]['last_name']
    author_first = emp.iloc[n]['first_name']
    author_middle = emp.iloc[n]['middle_name'] if (emp.iloc[n]['middle_name']!=None) else ""
    # author_middle = emp.iloc[n]['middle_name'] if (emp.iloc[n]['middle_name']!="None") else ""
    author_name = emp.iloc[n]['preferred_name']
    search_name = author_first + " " + author_middle + " "+ author_last if (emp.iloc[n]['middle_name']!=None) else author_first + " " + author_last
    # search_name = author_first + " " + author_middle + " "+ author_last if (emp.iloc[n]['middle_name']!="None") else author_first + " " + author_last
    # dept = emp.iloc[n]['department'] if (emp.iloc[n]['department']!="None") else ""
    dept = emp.iloc[n]['department'] if (emp.iloc[n]['department']!=None) else ""
    print(author_first + " " + author_middle + " "+ author_last)
    page_n = 1
    author_in = author_last +", "+author_first
    rec1 = get_wos_data_au(api_inst, page_n, author_in) 
    rec1_df = rec1.to_dict()
    if rec1_df['metadata']['total'] > 0:
        candidate_list = []
        candidate_list_id = []
        for work in range(len(rec1_df['hits'])):
            workX = rec1_df['hits'][work]['names']['authors']
            for authorX in workX:
                candidate_list.append(authorX['wosStandard'])
                if 'researcherId' in authorX:
                    candidate_list_id.append(authorX['researcherId'])
                else:
                    candidate_list_id.append(None)
        author_dict = dict(zip(candidate_list, candidate_list_id))
        candidate_list = list(author_dict.keys())
        # matches = {key: value for key, value in author_dict.items() if re.search(author_last, key)}
        # matches_list = list(matches.keys())
        # author_dict.get(closest_matches[0])
        # author_id = author_dict[closest_matches[0]]
        closest_matches = difflib.get_close_matches(author_in, candidate_list, n=5, cutoff=0.6)
        print(closest_matches)
        for match in closest_matches:   
            wos_id = author_dict.get(match)
            new_row = {'res_id': res_id, 'wos_id': wos_id, 'author_name': match, 'search_term': author_in}
            df = df._append(new_row, ignore_index=True)
            check_qry = "SELECT * FROM wos_lookup_history where res_id = {} AND wos_id = '{}'".format(res_id,wos_id)
            record = pd.read_sql(check_qry, con)
            if record.empty:
                qry = """INSERT INTO wos_lookup_history (res_id, wos_id, author_name, search_term) VALUES ({}, "{}","{}","{}")""".format(res_id, wos_id,match,author_in)
                con.execute(text(qry))
                con.commit()        
            check_qry = "SELECT * FROM id_lookup where res_id = {} AND wos_id='{}'".format(res_id, wos_id)
            record = pd.read_sql(check_qry, con)
            if record.empty:
                qry = "INSERT INTO id_lookup (res_id, wos_id) VALUES ({}, '{}')".format(res_id, wos_id)
                con.execute(text(qry))
                con.commit()
            # elif record['wos_id'][0] != wos_id:
            #     qry = "UPDATE id_lookup SET wos_id = '{}' WHERE emp_id = {}".format(author_id, emp_id)
            #     con.execute(text(qry))
            #     con.commit()
    else:
        print("No record found for "+ search_name)
        wos_id = None
        match = ""
        qry = """INSERT INTO wos_lookup_history (res_id, wos_id, author_name, search_term) VALUES ({}, "{}","{}","{}")""".format(res_id, wos_id,match,author_in)
        con.execute(text(qry))
        con.commit()

############################################################################################################
### Remove mismatching WOS names from wos_lookup_history and id_lookup
for n in range(0, len(emp)):
    res_id = int(emp.iloc[n]['res_id'])
    last_name = emp.iloc[n]['last_name']
    first_name = emp.iloc[n]['first_name']
    check_qry = """
                SELECT * FROM id_lookup where res_id = {}
                """.format(res_id)
    df = pd.read_sql(check_qry, con)
    if df.empty:
        continue
    else:
        for wos_id_n in range(len(df)):
            wos_id = df['wos_id'][wos_id_n]
            known_names = wos_get_known_names(api_inst, wos_id)
            known_names = list(set(known_names))
            if any(last_name in name for name in known_names): 
                if any(first_name[0] in name[0] for name in known_names):            
                    continue
                else:
                    remove_from_wos_lookup(con, res_id, df['wos_id'][wos_id_n])
            else:        
                remove_from_wos_lookup(con, res_id, df['wos_id'][wos_id_n])


############################################################################################################
### Find corresponding record from Open Alex
usd_alex_id = "https://openalex.org/I160856358"

for n in range(0,len(emp)):
    res_id = int(emp.iloc[n]['res_id'])
    author_last = emp.iloc[n]['last_name']
    author_first = emp.iloc[n]['first_name']
    # author_middle = emp.iloc[n]['middle_name'] if (emp.iloc[n]['middle_name']!="None") else ""
    author_middle = emp.iloc[n]['middle_name'] if (emp.iloc[n]['middle_name']!=None) else ""
    author_name = emp.iloc[n]['preferred_name']
    # search_name = author_first + " " + author_middle + " "+ author_last if (emp.iloc[n]['middle_name']!="None") else author_first + " " + author_last
    search_name = author_first + " " + author_middle + " "+ author_last if (emp.iloc[n]['middle_name']!=None) else author_first + " " + author_last
    dept = emp.iloc[n]['department'] if (emp.iloc[n]['department']!="None") else ""
    print(author_first + " " + author_middle + " "+ author_last)

    # specify endpoint
    endpoint = 'authors'
    filtered_works_url = f'https://api.openalex.org/{endpoint}?search={search_name}'

    loop_index = 0
    cursor_alex = "*"
    candidate_list = []
    candidate_list_id = []
    while cursor_alex:
        # set cursor value and request page from OpenAlex
        url = f'https://api.openalex.org/{endpoint}?search={search_name}&cursor={cursor_alex}'
        page_with_results = requests.get(url).json()
        if page_with_results['meta']['count']>0:
            results_page = page_with_results['results']
            for work in range(len(results_page)):
                authorX = results_page[work]
                if 'last_known_institutions' in authorX:
                    for i in range(len(authorX['last_known_institutions'])):
                        if authorX['last_known_institutions'][i]['id'] == usd_alex_id:
                            filtered_works_url = authorX['works_api_url']
                            candidate_list.append(authorX['display_name'])
                            alex_id = filtered_works_url.split(':')[-1]
                            candidate_list_id.append(alex_id)
        cursor_alex = page_with_results['meta']['next_cursor']
        loop_index += 1
        if loop_index in [5, 10, 20, 50, 100] or loop_index % 500 == 0:
            print(f'{loop_index} api requests made so far')

    # candidate_list = list(set(candidate_list))
    author_dict = dict(zip(candidate_list, candidate_list_id))

    if len(candidate_list)==0:
        print("No record found for "+ search_name)
        continue
    auth_data = []
    for author_index in range(len(author_dict)):
        author_n = author_dict.get(candidate_list[author_index])
        endpoint = 'authors'
        url = f'https://api.openalex.org/{endpoint}/{author_n}'
        page_with_results = requests.get(url).json()
        # page_with_results.keys()
        if page_with_results['id'] is not None:
            if page_with_results['last_known_institutions'] is not None:
                for affilation in page_with_results['last_known_institutions']:
                    auth_data.append({
                        'author_id': page_with_results['id'],
                        'orcid': page_with_results['orcid'],
                        'display_name': page_with_results['display_name'],
                        'display_name_alternatives': page_with_results['display_name_alternatives'],
                        'works_count': page_with_results['works_count'],
                        'affiliation_id': affilation['id'],
                        'affiliation_name': affilation['display_name'],      
                    })

    auth_df = pd.DataFrame(auth_data)
    auth_df = auth_df[auth_df['affiliation_id'] == usd_alex_id]
    auth_df['works_count'] = auth_df['works_count'].astype(int)
    
    #### Get the name from WOS
    if len(auth_df)>1:
        print("More than one record found for "+ search_name)
        #### Does the person have a WOS ID?
        check_qry = "SELECT * FROM id_lookup where res_id = '{}'".format(res_id)
        record = pd.read_sql(check_qry, con)
        record = record[(record['wos_id']!="None") & (record['alex_id']!="None")]
        record = record.drop_duplicates(subset=['res_id', 'wos_id', 'alex_id'])
        print("check1")
        if (not record.empty) and (record['wos_id'].all() !='None'):
            print("check2")
            first_wos_id = record['wos_id'] if len(record['wos_id'])==1 else record['wos_id'][0]
            wos_check = get_wos_data_ai(api_inst, 1, first_wos_id).to_dict()
            wos_check_candidate_list = []
            wos_check_candidate_list_wos = []
            for work in range(len(wos_check['hits'])):
                workX = wos_check['hits'][work]['names']['authors']
                for authorX in workX:  
                    if ('researcherId' in authorX) and authorX['researcherId'] ==record['wos_id'][0]:
                        wos_check_candidate_list.append(authorX['displayName'])
                        wos_check_candidate_list_wos.append(authorX['wosStandard'])
            wos_check_candidate_list = list(set(wos_check_candidate_list))
            wos_check_candidate_list_wos = list(set(wos_check_candidate_list_wos))
            # matches = {key: value for key, value in author_dict.items() if re.search(author_last, key)}
            # matches_list = list(matches.keys())            
            wos_check_candidate_list = wos_check_candidate_list + wos_check_candidate_list_wos
            for name in range(len(wos_check_candidate_list)):
                parts = wos_check_candidate_list[name].split(', ')
                if len(parts)>=2:
                    wos_check_candidate_list[name] = f"{parts[1]} {parts[0]}"
            closest_matches = difflib.get_close_matches(search_name, wos_check_candidate_list, n=1, cutoff=0.6)
            if len(closest_matches)>0:
                closest_matches = difflib.get_close_matches(closest_matches[0], author_dict.keys(), n=1, cutoff=0.6)
                author_id = author_dict.get(closest_matches[0])
                auth_df = auth_df[auth_df['author_id'] == "https://openalex.org/"+author_id]
        
        # if int(auth_df['orcid'].isnull().sum())==len(auth_df):    
        #     X = get_wos_data_au(api_inst, 1, author_in)
        #     X = X.to_dict()
        #     rec1 = get_wos_data_au(api_inst, page_n, author_in) 
        #     rec1_df = rec1.to_dict()
        #     #### Get the name from WOS?
        #     check_qry = "SELECT * FROM id_lookup where emp_id = '{}'".format(emp_id)
        #     record = pd.read_sql(check_qry, con)
        #     auth_df = auth_df[auth_df['orcid'].notnull()]

    # if len(auth_df)>1:
    #     auth_df = auth_df.iloc[auth_df['works_count'].idxmax()]
    #     print("After orcid: "+ search_name)
    
    ### Case where there is multiple Open Alex IDs but no WOS record
    if (len(auth_df)>1):
        for open_n in range(len(auth_df)):
            alex_id = auth_df['author_id'].values[open_n].split('/')[-1] 
            qry = "INSERT INTO id_lookup (res_id, alex_id) VALUES ({}, '{}')".format(res_id, alex_id)
            con.execute(text(qry))
            con.commit()

    # if len(auth_df)>1:
    #     print("Still too many records: "+ search_name)
    #     break

    alex_id = auth_df['author_id'].values[0].split('/')[-1]
    
    check_qry = "SELECT * FROM id_lookup where res_id = '{}'".format(res_id)
    record = pd.read_sql(check_qry, con)
    if record.empty:
        print('Inserting record for '+ search_name)
        qry = "INSERT INTO id_lookup (res_id, alex_id) VALUES ({}, '{}')".format(res_id, alex_id)
        con.execute(text(qry))
    elif record['alex_id'][0] != alex_id:
        print('Updating record for '+ search_name)
        qry = "UPDATE id_lookup SET alex_id = '{}' WHERE res_id = {}".format(alex_id, res_id)
        con.execute(text(qry))
    else:
        wos_id = record['wos_id'][0]
        qry1 = "UPDATE id_lookup SET alex_id = '{}' WHERE res_id = {}".format(alex_id, res_id)
        # qry1 = "DELETE FROM id_lookup WHERE res_id ={}".format(res_id)
        con.execute(text(qry1))
        # qry2 = "INSERT INTO id_lookup (res_id, wos_id, alex_id) VALUES ("+str(res_id)+",'"+wos_id+"','"+alex_id+"')"
        # con.execute(text(qry2))
    con.commit()


############################################################################################################
### Manual removals

WOS_id_removals =[]
WOS_id_removals.append('LHR-4633-2024')
for id_remv in WOS_id_removals:
    qry = "DELETE FROM id_lookup WHERE wos_id='{}'".format(id_remv)
    con.execute(text(qry))
    con.commit()


emp_id = 46
res_id = 2
check_qry = "SELECT * FROM id_lookup where res_id = {}".format(res_id)
# check_qry = "SELECT * FROM id_lookup" 
record = pd.read_sql(check_qry, con)


get_wos_data_ai(api_inst, page_n, record['wos_id'][0]) if record['wos_id'][0] != None else None

record

check_qry = "SELECT * FROM emp_tbl"
record = pd.read_sql(check_qry, con)
# record.to_pickle('Data/CAS.pkl')

x1 = get_wos_data_au(api_inst, 1, 'JKO-0584-2023')
x1 = x1.to_dict()
x1['metadata']['total']