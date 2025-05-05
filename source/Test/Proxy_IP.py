import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import pandas as pd
import random

proxies_list = [
"185.188.78.211:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"186.179.0.106:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"141.98.153.228:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"104.239.118.63:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"181.177.77.67:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"185.196.190.179:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"181.177.78.234:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"104.233.48.228:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"178.212.35.225:3199:mariyarathna-z4kxz:Fh4XiNMb3I",
"181.177.77.19:3199:mariyarathna-z4kxz:Fh4XiNMb3I"
]

formatted_proxies = []
for proxy in proxies_list:
    ip, port, user, password = proxy.split(':')
    formatted_proxy = f'http://{user}:{password}@{ip}:{port}'
    formatted_proxies.append({'http': formatted_proxy, 'https': formatted_proxy})

def get_random_proxy():
    return random.choice(formatted_proxies)

def get_soup(url):
    response = requests.get(url,proxies=get_random_proxy())
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

url='http://www.medscimonit.com/medscimonit/'

soup=get_soup(url)
print(soup)