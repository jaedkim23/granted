import pandas as pd
from dotenv import load_dotenv
from mysql.connector import Error
import datetime
import requests
import clarivate.wos_starter.client
from clarivate.wos_starter.client.rest import ApiException
from sqlalchemy import create_engine, text

current_year = datetime.datetime.now().year

def create_record_tbl_alex(author_id_in):
    ### WOS records
    ### Check if there is no matching WOS id first
    usd_alex_id = "https://openalex.org/I160856358"
    pub_alex = get_open_alex_data_ai(author_id_in)
    pub_alex = pub_alex.loc[pub_alex['institution_id'] == usd_alex_id]
    pub_alex = pub_alex[['work_id', 'work_title', 'work_publication_year', 'work_source']]
    return pub_alex

def create_record_tbl(author_id_in, api_param_in):
    #######################################################################
    # Input: author_id_in is a dataframe with author ids
    #        api_param_in is the api instance
    # OUtput: pub_df is a dataframe with the publication records
    # This function returns the list of publication records for the given author id in the WOS database

    ### Check if there is no matching WOS id first
    pub_df=[]
    for author_n in range(len(author_id_in)):
        author_wos_id = author_id_in[author_n]
        rec1_df = get_wos_data_ai(api_param_in, 1, author_wos_id).to_dict()
        n_records = rec1_df['metadata']['total']
        ### if there is more than 1 record:
        if n_records > 1:
            n_limit = rec1_df['metadata']['limit']
            page = range(1, n_records//n_limit+2)
            data = []
            for page_n in page:
                rec1_df = get_wos_data_ai(api_param_in, page_n, author_wos_id).to_dict() 
                for index in range(len(rec1_df['hits'])):
                    if 'doi' in rec1_df['hits'][index]['identifiers']:
                        doi = rec1_df['hits'][index]['identifiers']['doi']
                    else:
                        doi = None
                    if 'issn' in rec1_df['hits'][index]['identifiers']:
                        issn = rec1_df['hits'][index]['identifiers']['issn']
                    else:
                        issn = None
                    if 'eissn' in rec1_df['hits'][index]['identifiers']:
                        eissn = rec1_df['hits'][index]['identifiers']['eissn']
                    else:
                        eissn = None
                    pub_df.append({
                        'work_id': rec1_df['hits'][index]['uid'].split(':')[1],
                        'title': rec1_df['hits'][index]['title'],
                        'source': rec1_df['hits'][index]['source']['sourceTitle'],
                        'publishYear': rec1_df['hits'][index]['source']['publishYear'],
                        'doi': doi,
                        'issn': issn,
                        'eissn': eissn,
                        })
    pub_df = pd.DataFrame(pub_df)
    return pub_df

def get_wos_data_au(api_instance, page_n, author):
    #######################################################################
    # Default function call to WOS to retrieve the publication records for the given author and USD post year 2000
    # Output: DocumentsList response from Clarivate API

    q = f'AU={author} AND OG=University of San Diego AND PY=(2000-{current_year})' # str | Web of Science advanced [advanced search query builder](https://webofscience.help.clarivate.com/en-us/Content/advanced-search.html). The supported field tags are listed in description.
    db = 'WOS' # str | Web of Science Database abbreviation * WOS - Web of Science Core collection * BIOABS - Biological Abstracts * BCI - BIOSIS Citation Index * BIOSIS - BIOSIS Previews * CCC - Current Contents Connect * DIIDW - Derwent Innovations Index * DRCI - Data Citation Index * MEDLINE - MEDLINE The U.S. National Library of Medicine® (NLM®) premier life sciences database. * ZOOREC - Zoological Records * PPRN - Preprint Citation Index * WOK - All databases  (optional) (default to 'WOS')
    limit = 50 # int | set the limit of records on the page (1-50) (optional) (default to 10)
    page = page_n # int | set the result page (optional) (default to 1)
    sort_field = 'LD+D' # str | Order by field(s). Field name and order by clause separated by '+', use A for ASC and D for DESC, ex: PY+D. Multiple values are separated by comma. Supported fields:  * **LD** - Load Date * **PY** - Publication Year * **RS** - Relevance * **TC** - Times Cited  (optional)
    modified_time_span = None # str | Defines a date range in which the results were most recently modified. Beginning and end dates must be specified in the yyyy-mm-dd format separated by '+' or ' ', e.g. 2023-01-01+2023-12-31. This parameter is not compatible with the all databases search, i.e. db=WOK is not compatible with this parameter. (optional)
    tc_modified_time_span = None # str | Defines a date range in which times cited counts were modified. Beginning and end dates must be specified in the yyyy-mm-dd format separated by '+' or ' ', e.g. 2023-01-01+2023-12-31. This parameter is not compatible with the all databases search, i.e. db=WOK is not compatible with this parameter. (optional)
    detail = None # str | it will returns the full data by default, if detail=short it returns the limited data (optional)

    try:
        # Query Web of Science documents 
        api_response = api_instance.documents_get(q, db=db, limit=limit, page=page, sort_field=sort_field, modified_time_span=modified_time_span, tc_modified_time_span=tc_modified_time_span, detail=detail)
        return api_response
        # print("The response of DocumentsApi->documents_get:\n")
        # pprint(api_response)
    except ApiException as e:
        return print("Exception when calling DocumentsApi->documents_get: %s\n" % e)
    
def get_wos_data_ai(api_instance, page_n, author_id):
    #######################################################################
    # Default function call to WOS to retrieve the publication records for the given WOS author ID
    # Output: DocumentsList response from Clarivate API
    
    q = f'AI={author_id}' # str | Web of Science advanced [advanced search query builder](https://webofscience.help.clarivate.com/en-us/Content/advanced-search.html). The supported field tags are listed in description.
    db = 'WOS' # str | Web of Science Database abbreviation * WOS - Web of Science Core collection * BIOABS - Biological Abstracts * BCI - BIOSIS Citation Index * BIOSIS - BIOSIS Previews * CCC - Current Contents Connect * DIIDW - Derwent Innovations Index * DRCI - Data Citation Index * MEDLINE - MEDLINE The U.S. National Library of Medicine® (NLM®) premier life sciences database. * ZOOREC - Zoological Records * PPRN - Preprint Citation Index * WOK - All databases  (optional) (default to 'WOS')
    limit = 50 # int | set the limit of records on the page (1-50) (optional) (default to 10)
    page = page_n # int | set the result page (optional) (default to 1)
    sort_field = 'LD+D' # str | Order by field(s). Field name and order by clause separated by '+', use A for ASC and D for DESC, ex: PY+D. Multiple values are separated by comma. Supported fields:  * **LD** - Load Date * **PY** - Publication Year * **RS** - Relevance * **TC** - Times Cited  (optional)
    modified_time_span = None # str | Defines a date range in which the results were most recently modified. Beginning and end dates must be specified in the yyyy-mm-dd format separated by '+' or ' ', e.g. 2023-01-01+2023-12-31. This parameter is not compatible with the all databases search, i.e. db=WOK is not compatible with this parameter. (optional)
    tc_modified_time_span = None # str | Defines a date range in which times cited counts were modified. Beginning and end dates must be specified in the yyyy-mm-dd format separated by '+' or ' ', e.g. 2023-01-01+2023-12-31. This parameter is not compatible with the all databases search, i.e. db=WOK is not compatible with this parameter. (optional)
    detail = None # str | it will returns the full data by default, if detail=short it returns the limited data (optional)

    try:
        # Query Web of Science documents 
        api_response = api_instance.documents_get(q, db=db, limit=limit, page=page, sort_field=sort_field, modified_time_span=modified_time_span, tc_modified_time_span=tc_modified_time_span, detail=detail)
        return api_response
        # print("The response of DocumentsApi->documents_get:\n")
        # pprint(api_response)
    except ApiException as e:
        return print("Exception when calling DocumentsApi->documents_get: %s\n" % e)

def get_open_alex_data_ai(id_in):
    endpoint = 'authors'
    filtered_works_url = f'https://api.openalex.org/works?filter=author.id:{id_in}'
    page_with_results = requests.get(filtered_works_url).json()
    # page_with_results['meta']
    # works = page_with_results['results']

    cursor_alex = '*'

    select = ",".join((
        'id',
        'ids',
        'title',
        'display_name',
        'publication_year',
        'publication_date',
        'primary_location',
        'open_access',
        'authorships',
        'cited_by_count',
        'is_retracted',
        'is_paratext',
        'updated_date',
        'created_date',
    ))

    # loop through pages
    works = []
    loop_index = 0
    while cursor_alex:
        # set cursor value and request page from OpenAlex
        url = f'{filtered_works_url}&select={select}&cursor={cursor_alex}'
        page_with_results = requests.get(url).json()
        
        results = page_with_results['results']
        works.extend(results)

        # update cursor to meta.next_cursor
        cursor_alex = page_with_results['meta']['next_cursor']
        loop_index += 1
        if loop_index in [5, 10, 20, 50, 100] or loop_index % 500 == 0:
            print(f'{loop_index} api requests made so far')
    print(f'done. made {loop_index} api requests. collected {len(works)} works')

    data = []
    for work in works:
        if work['primary_location'] != None:
            if work['primary_location']["source"] != None:
                source_display_name = work['primary_location']['source']['display_name']
        else:
            source_display_name = None
        for authorship in work['authorships']:
            if authorship:
                author = authorship['author']
                author_id = author['id'] if author else None
                author_name = author['display_name'] if author else None
                author_position = authorship['author_position']
                for institution in authorship['institutions']:
                    if institution:
                        institution_id = institution['id']
                        institution_name = institution['display_name']
                        institution_country_code = institution['country_code']
                        data.append({
                            'work_id': work['id'],
                            'work_title': work['title'],
                            'work_display_name': work['display_name'],
                            'work_publication_year': work['publication_year'],
                            'work_publication_date': work['publication_date'],
                            'work_source': source_display_name,
                            'author_id': author_id,
                            'author_name': author_name,
                            'author_position': author_position,
                            'institution_id': institution_id,
                            'institution_name': institution_name,
                            'institution_country_code': institution_country_code,
                        })
    pub_alex = pd.DataFrame(data)
    pub_alex = pub_alex[pub_alex['author_id'] == 'https://openalex.org/'+id_in]
    return pub_alex

def find_lookup_record(author_in):
    author_record = emp[emp['preferred_name']==author_in]
    author_record = id_lookup[id_lookup['emp_id']==int(author_record['emp_id'].values[0])]
    # author_record = author_record['wos_id'].to_list()
    return author_record

def find_common_records(df1_wos, df2_alex):
    if isinstance(df1_wos, pd.DataFrame):
        df_wos_sub = df1_wos[['title','source','publishYear']].copy()
        df_wos_sub['title'] = df_wos_sub['title'].str.lower()
        df_wos_sub['source'] = df_wos_sub['source'].str.lower()    
    else:
        df_wos_sub = 0
    
    if isinstance(df2_alex, pd.DataFrame):
        df_alex_sub = df2_alex[['work_title','work_source','work_publication_year']].copy()
        df_alex_sub['work_source'] = df_alex_sub['work_source'].str.lower()
        df_alex_sub['work_title'] = df_alex_sub['work_title'].str.lower()
        df_alex_sub.columns = ['title','source','publishYear']
    else:
        df_alex_sub = 0

    if (isinstance(df_wos_sub, pd.DataFrame)) and (isinstance(df_alex_sub, pd.DataFrame)):
        df_combined = pd.concat([df_wos_sub, df_alex_sub], axis=0)
        df_combined = df_combined.drop_duplicates(subset=['title','publishYear'], keep=False)
    elif isinstance(df_wos_sub, pd.DataFrame) and (df_alex_sub == 0):
        df_combined = df_wos_sub
    elif (df_wos_sub == 0) and (isinstance(df_alex_sub, pd.DataFrame)):
        df_combined = df_alex_sub
    else:
        df_combined = 0
    return df_combined

def wos_get_known_names(api_instance, author_id):
    try:
        api_response = get_wos_data_ai(api_instance, 1, author_id)
        wos_check=api_response.to_dict()
        wos_check_candidate_list = []
        wos_check_candidate_list_wos = []
        for work in range(len(wos_check['hits'])):
            workX = wos_check['hits'][work]['names']['authors']
            for authorX in workX:  
                if ('researcherId' in authorX) and authorX['researcherId'] ==author_id:
                    wos_check_candidate_list.append(authorX['displayName'])
                    wos_check_candidate_list_wos.append(authorX['wosStandard'])
        wos_check_candidate_list = list(set(wos_check_candidate_list))
        wos_check_candidate_list_wos = list(set(wos_check_candidate_list_wos))
        wos_check_candidate_list = wos_check_candidate_list + wos_check_candidate_list_wos
        for name in range(len(wos_check_candidate_list)):
                parts = wos_check_candidate_list[name].split(', ')
                if len(parts)>=2:
                    wos_check_candidate_list[name] = f"{parts[1]} {parts[0]}"
        return wos_check_candidate_list
    except ApiException as e:
        return print("Exception when calling DocumentsApi->documents_get: %s\n" % e)

def remove_from_wos_lookup(con_df, employee, wos_record):
    qry = "DELETE FROM wos_lookup_history WHERE emp_id = {} AND wos_id = '{}'".format(employee, wos_record)
    con_df.cursor().execute(qry)
    con_df.commit()
    qry = "DELETE FROM id_lookup WHERE emp_id = {} AND wos_id = '{}'".format(employee, wos_record)
    con_df.cursor().execute(qry)
    con_df.commit()

def get_open_alex_data_ai(id_in):
    endpoint = 'authors'
    filtered_works_url = f'https://api.openalex.org/works?filter=author.id:{id_in}'
    page_with_results = requests.get(filtered_works_url).json()
    # page_with_results['meta']
    # works = page_with_results['results']

    cursor_alex = '*'

    select = ",".join((
        'id',
        'ids',
        'title',
        'display_name',
        'publication_year',
        'publication_date',
        'primary_location',
        'open_access',
        'authorships',
        'cited_by_count',
        'is_retracted',
        'is_paratext',
        'updated_date',
        'created_date',
    ))

    # loop through pages
    works = []
    loop_index = 0
    while cursor_alex:
        # set cursor value and request page from OpenAlex
        url = f'{filtered_works_url}&select={select}&cursor={cursor_alex}'
        page_with_results = requests.get(url).json()
        
        results = page_with_results['results']
        works.extend(results)

        # update cursor to meta.next_cursor
        cursor_alex = page_with_results['meta']['next_cursor']
        loop_index += 1
        if loop_index in [5, 10, 20, 50, 100] or loop_index % 500 == 0:
            print(f'{loop_index} api requests made so far')
    print(f'done. made {loop_index} api requests. collected {len(works)} works')

    data = []
    for work in works:
        if work['primary_location']['source'] != None:
            source_display_name = work['primary_location']['source']['display_name']
        else:
            source_display_name = None
        for authorship in work['authorships']:
            if authorship:
                author = authorship['author']
                author_id = author['id'] if author else None
                author_name = author['display_name'] if author else None
                author_position = authorship['author_position']
                for institution in authorship['institutions']:
                    if institution:
                        institution_id = institution['id']
                        institution_name = institution['display_name']
                        institution_country_code = institution['country_code']
                        data.append({
                            'work_id': work['id'],
                            'work_title': work['title'],
                            'work_display_name': work['display_name'],
                            'work_publication_year': work['publication_year'],
                            'work_publication_date': work['publication_date'],
                            'work_source': source_display_name,
                            'author_id': author_id,
                            'author_name': author_name,
                            'author_position': author_position,
                            'institution_id': institution_id,
                            'institution_name': institution_name,
                            'institution_country_code': institution_country_code,
                        })
    pub_alex = pd.DataFrame(data)
    pub_alex = pub_alex[pub_alex['author_id'] == 'https://openalex.org/'+id_in]
    return pub_alex

