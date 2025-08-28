import time
import requests

# Base URL for Crossref API
base_url = "https://api.crossref.org"

# Add headers (polite pool - recommended)
headers = {
    'User-Agent': 'Your-App-Name/1.0 (mailto:your-email@domain.com)'
}

# 1. Search for works by title
def search_crossref_by_title(title):
    url = f"{base_url}/works"
    params = {
        'query.title': title,
        'rows': 10  # Number of results to return
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# 2. Get work by DOI
def get_crossref_by_doi(doi):
    url = f"{base_url}/works/{doi}"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# 3. Search by author
def search_crossref_by_author(author_name):
    url = f"{base_url}/works"
    params = {
        'query.author': author_name,
        'rows': 20
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
