from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

session = HTMLSession()

url = "http://www.cjee.ac.cn/en/hjgcxb/article/archives"
base_url = "http://www.cjee.ac.cn/"

response = session.get(url, headers=headers)
response.html.render(sleep=5)

html_content = response.html.html

print(html_content)
