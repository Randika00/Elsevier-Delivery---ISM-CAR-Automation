import requests
from bs4 import BeautifulSoup

headers = {
    # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "accept-encoding": "gzip, deflate, br, zstd",
    # "accept-language": "en-US,en;q=0.9",
    # "cache-control": "max-age=0",
    # "connection": "keep-alive",
    # "cookie": "Hm_lvt_499fe66018ba124742223771bafcf3be=1727258336; HMACCOUNT=D8B913D5CBCBAC73; Hm_lpvt_499fe66018ba124742223771bafcf3be=1727258393",
    # "host": "zrxuebao.njust.edu.cn",
    # "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    # "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": '"Windows"',
    # "sec-fetch-dest": "document",
    # "sec-fetch-mode": "navigate",
    # "sec-fetch-site": "same-origin",
    # "sec-fetch-user": "?1",
    # "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}


def get_soup(url):
    # curl=f"http://api.scraperapi.com?api_key=9c5044e75f177a7c90a667bc3123207b&url={url}"
    # response = requests.get(curl,headers=headers)
    response = requests.get(url, headers=headers)
    response_code=response.status_code
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup,response_code

url="https://www.sap.org.ar/publicaciones/archivos/numero-actual.html"
soup=get_soup(url)
print(soup)