import requests
from bs4 import BeautifulSoup

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

url = "http://ytlx.whrsm.ac.cn/EN/1000-7598/home.shtml"
base_url = "http://ytlx.whrsm.ac.cn/EN"
response = requests.get(url, headers=headers)
link = BeautifulSoup(response.content, "html.parser").find("div", class_="left_tab_zxqk").findAll("li")[1].find("a").get("href")

print(link)

