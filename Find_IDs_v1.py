import pandas as pd
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
import requests
import datetime
from common_func import *
import difflib

api = '1228ec5f8a29051d5dd8a7fbbd01a114d6de7ef1'

con = mysql.connector.connect(
    host='',
    database='',
    user='',
    password=''
)

cursor = con.cursor()

qry  = "SELECT * FROM emp_cas"
CAS = pd.read_sql(qry, con)

search_words = ['Professor', 'Assistant Professor', 'Associate Professor', 'Lecturer']
pattern = '|'.join(search_words)
emp = CAS[CAS['position'].str.contains(pattern, case=False, na=False)]

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

# for n in range(0, len(emp)):
for n in range(0, len(emp)):
    df = pd.DataFrame(columns=['emp_id', 'wos_id', 'author_name', 'search_term'])
    emp_id = int(emp.iloc[n]['emp_id'])
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
            new_row = {'emp_id': emp_id, 'wos_id': wos_id, 'author_name': match, 'search_term': author_in}
            df = df._append(new_row, ignore_index=True)
            check_qry = "SELECT * FROM wos_lookup_history where emp_id = {} AND wos_id = '{}'".format(emp_id,wos_id)
            record = pd.read_sql(check_qry, con)
            if record.empty:
                qry = """INSERT INTO wos_lookup_history (emp_id, wos_id, author_name, search_term) VALUES ({}, "{}","{}","{}")""".format(emp_id, wos_id,match,author_in)
                cursor.execute(qry)
                con.commit()        
            check_qry = "SELECT * FROM id_lookup where emp_id = {} AND wos_id='{}'".format(emp_id, wos_id)
            record = pd.read_sql(check_qry, con)
            if record.empty:
                qry = "INSERT INTO id_lookup (emp_id, wos_id) VALUES ({}, '{}')".format(emp_id, wos_id)
                cursor.execute(qry)
                con.commit()
    else:
        print("No record found for "+ search_name)
        wos_id = None
        match = ""
        qry = """INSERT INTO wos_lookup_history (emp_id, wos_id, author_name, search_term) VALUES ({}, "{}","{}","{}")""".format(emp_id, wos_id,match,author_in)
        cursor.execute(qry)
        con.commit()

############################################################################################################
### Remove mismatching WOS names from wos_lookup_history and id_lookup
for n in range(0, len(emp)):
    emp_id = int(emp.iloc[n]['emp_id'])
    last_name = emp.iloc[n]['last_name']
    first_name = emp.iloc[n]['first_name']
    check_qry = "SELECT * FROM id_lookup where emp_id = {}".format(emp_id)
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
                    remove_from_wos_lookup(con, emp_id, df['wos_id'][wos_id_n])
            else:        
                remove_from_wos_lookup(con, emp_id, df['wos_id'][wos_id_n])


############################################################################################################
### Find corresponding record from Open Alex
usd_alex_id = "https://openalex.org/I160856358"

for n in range(len(emp)):
    emp_id = int(emp.iloc[n]['emp_id'])
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
        check_qry = "SELECT * FROM id_lookup where emp_id = '{}'".format(emp_id)
        record = pd.read_sql(check_qry, con)
        if record['wos_id'][0] is not None:
            wos_check=get_wos_data_ai(api_inst, 1, record['wos_id'][0]).to_dict()
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
            wos_check_candidate_list = wos_check_candidate_list + wos_check_candidate_list_wos
            for name in range(len(wos_check_candidate_list)):
                parts = wos_check_candidate_list[name].split(', ')
                if len(parts)>=2:
                    wos_check_candidate_list[name] = f"{parts[1]} {parts[0]}"
            closest_matches = difflib.get_close_matches(search_name, wos_check_candidate_list, n=1, cutoff=0.6)
            closest_matches = difflib.get_close_matches(closest_matches[0], author_dict.keys(), n=1, cutoff=0.6)
            author_id = author_dict.get(closest_matches[0])
            auth_df = auth_df[auth_df['author_id'] == "https://openalex.org/"+author_id]
        
    if len(auth_df)>1:
        print("Still too many records: "+ search_name)
        break

    alex_id = auth_df['author_id'].values[0].split('/')[-1]
    
    check_qry = "SELECT * FROM id_lookup where emp_id = '{}'".format(emp_id)
    record = pd.read_sql(check_qry, con)
    if record.empty:
        print('Inserting record for '+ search_name)
        qry = "INSERT INTO id_lookup (emp_id, alex_id) VALUES ({}, '{}')".format(emp_id, alex_id)
        con.cursor().execute(qry)
    elif record['alex_id'][0] != alex_id:
        print('Updating record for '+ search_name)
        qry = "UPDATE id_lookup SET alex_id = '{}' WHERE emp_id = {}".format(alex_id, emp_id)
        con.cursor().execute(qry)
    else:
        wos_id = record['wos_id'][0]
        qry1 = "UPDATE id_lookup SET alex_id = '{}' WHERE emp_id = {}".format(alex_id, emp_id)
        con.cursor().execute(qry1)
    con.commit()

