import requests
from bs4 import BeautifulSoup
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

proxies_list = [
   "141.98.155.137:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "185.205.199.161:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "216.10.5.126:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "2.58.80.143:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "185.207.96.233:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "67.227.121.110:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "67.227.127.100:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "181.177.76.122:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "185.207.97.85:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "186.179.21.77:3199:mariyarathna-dh3w3:IxjkW0fdJy"
]

formatted_proxies = [{'http': f'http://{proxy.split(":")[2]}:{proxy.split(":")[3]}@{proxy.split(":")[0]}:{proxy.split(":")[1]}'} for proxy in proxies_list]

def get_random_proxy():
    return random.choice(formatted_proxies)

def get_soup(url):
    my_proxy = get_random_proxy()
    print(my_proxy)
    response = requests.get(url, headers=headers, proxies=my_proxy)
    print(response)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_public_ip():
    try:
        my_proxy = get_random_proxy()
        response = requests.get('http://api.ipify.org?format=json', proxies=my_proxy)
        if response.status_code == 200:
            print(response.json()['ip'])
            return response.json()['ip']
        else:
            return 'Error: Unable to fetch IP address'
    except Exception as e:
        return f'Error: {str(e)}'

public_ip = get_public_ip()
print('Your public IP address is:', public_ip)