import requests
import pandas as pd
from io import BytesIO

### Each year has a different 5-digit identifier
year = 2023 
year_id = 24308

tabx_sub1 = "https://ncses.nsf.gov/pubs/nsf"
tabx_sub2 = "/assets/data-tables/tables/nsf"

tabs = []
tab1_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab001.xlsx"
tabs.append(tab1_link)
tab2_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab002.xlsx"
tabs.append(tab2_link)
tab3_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab003.xlsx"
tabs.append(tab3_link)
tab9_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab009.xlsx"
tabs.append(tab9_link)
tab10_link = tabx_sub1+str(year_id)+tabx_sub2+str(year_id)+"-tab010.xlsx"
tabs.append(tab10_link)

tabs
# The link should be of the file directly
url = tabs[0]

r = requests.get(url)
if r.status_code == 200:
    excel_data= BytesIO(r.content)
    df = pd.read_excel(excel_data)
else:
     print(f"Failed to download the file. Status code: {r.status_code}")


file_extension = '.<file extension>'   # Example .wav
r = requests.get(url)

# If extension does not exist in end of url, append it
if file_extension not in url.split("/")[-1]:
        filename = f'{last_url_path}{file_extension}'
# Else take the last part of the url as filename
else:
        filename = url.split("/")[-1]

with open(filename, 'wb') as f:
        # You will get the file in base64 as content
        f.write(r.content)