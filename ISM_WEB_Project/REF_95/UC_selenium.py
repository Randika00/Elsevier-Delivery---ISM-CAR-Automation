import re
import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pandas as pd
import chromedriver_autoinstaller as chromedriver
import json

headers = {
    "Cookie": "AJOT2_SessionId=pggqus1ldfo0bwzneawsxjev; American_Occupational_Therapy_AssociationMachineID=638465226214394544; _ga=GA1.3.913198106.1710925824; _gid=GA1.3.1309327130.1710925824; hubspotutk=45c7ea6f7f9bc84af981be5458cbd84f; __hssrc=1; _gcl_au=1.1.585721882.1710925826; _ga=GA1.1.913198106.1710925824; fpestid=4kF3LjnaKNrsHvB8tW4_YKTLTPNsD6vCuAlY0WCMKU5aAwe6XWWv6UtXpHzRbXLsSv41wA; _fbp=fb.1.1710925826667.1584579234; sa-user-id=s%253A0-e2678d88-10ca-5085-6e7f-9699543ec39e.aIOhjYU93e7TrKIeWR6gMMmTxJ02LKzL9HBy03tu1O8; sa-user-id-v2=s%253A4meNiBDKUIVuf5aZVD7DnsD4CYs.VtEorakjnt%252FJQzeCUbY79ctfGiblf2HOIqPboSWhdv8; sa-user-id-v3=s%253AAQAKIDXsHk-nPieIBwxcewSN2DK_yU_oPgQnkfXYHwGkT2yaEAEYAyCIiJCuBjABOgQhyhL0QgRXNvD_.c4W0g0ObZSPQuXL6BfKED0nlq%252BmsAqIVpcRJoitHQOc; _clck=1vryupj%7C2%7Cfk9%7C0%7C1540; AOTATest=ok; visid_incap_531175=Zy2nzuSmR5yFKFg6O/LRzFEC/GUAAAAAQUIPAAAAAAAwq1h6OkWoDAVnjInquuek; incap_ses_1789_531175=z+8RXSSzxndaBkzgDs7TGFIC/GUAAAAAadGLWY1wNHMxfyo/d3eR9w==; __hstc=204606671.45c7ea6f7f9bc84af981be5458cbd84f.1710925825505.1711010287800.1711014485331.3; __hssc=204606671.3.1711014485331; _uetsid=b08c93e0e69911ee8a2b1968b6f72485; _uetvid=b08cc970e69911ee91acfbf279c55fdb; _clsk=f67khb%7C1711015485276%7C7%7C1%7Ck.clarity.ms%2Fcollect; _ga_3CVRFYYS90=GS1.1.1711012705.3.1.1711015489.58.0.0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
#chromedriver.install()
def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup
def get_driver_content(url):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("window-size=1400,600")
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        driver.get(url)
        content = driver.page_source
        cookies = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in driver.get_cookies()])
        soup = BeautifulSoup(content, 'html.parser')
        return soup, cookies
    finally:
        time.sleep(2)
        driver.close()
        driver.quit()

url='https://gdnykx.cnjournals.org/gdnykxen/ch/reader/issue_list.aspx?year_id=2024&quarter_id=2'
soup,cookies = get_driver_content(url)
# pdf_link="https://research.aota.org"+soup.find("li",class_="toolbar-item item-with-dropdown item-pdf").find("a").get("href")
print(soup)