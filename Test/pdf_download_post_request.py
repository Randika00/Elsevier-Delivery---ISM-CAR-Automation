import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import pandas as pd

out_path='Out'
if not os.path.exists(out_path):
    os.makedirs(out_path)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

out_folder=os.path.join(out_path,'New.pdf')

pdf_link="https://www.ingentaconnect.com/cdn-cgi/rum?"

# payload={"siteToken": "1468a68d648449d987ed5f15341e1865",
#          "pageloadId":"414ae589-0ba0-4570-930b-f500aa7bca01",
#         # "referrer":"https://www.ingentaconnect.com/content/scimed/mppa/2024/00000039/00000001;jsessionid=7ti9gaal0cc5j.x-ic-live-03",
#         # "location":"https://www.ingentaconnect.com/contentone/scimed/mppa/2024/00000039/00000001/art00003"
#          }
payload={"siteToken": "1468a68d648449d987ed5f15341e1865"}

pdf_content = requests.post(pdf_link,data=payload,headers=headers).content
with open(out_folder, 'wb') as file:
    file.write(pdf_content)