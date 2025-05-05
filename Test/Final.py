import cloudscraper
from bs4 import BeautifulSoup
import requests
from random import randint
from time import sleep
import os
import sys
import re

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def ret_file_name_full(text, extention):
    exe_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
    out_path = os.path.join(exe_folder, 'in')
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    index = 1
    outFileName = os.path.join(out_path, remove_invalid_paths(text) + extention)
    retFileName = outFileName
    while os.path.isfile(retFileName):
        retFileName = os.path.join(out_path, remove_invalid_paths(text) + "_" + str(index) + extention)
        index += 1
    return retFileName

def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|\n]', "_", path_val)

url='https://research.aota.org/ajot/article-pdf/78/4/7804185050/84913/7804185050.pdf'
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'ScraperBot/1.0',
    }
)
response = scraper.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
current_links=soup.find('div', class_='table-of-content').find_all('div', class_='issue-item')
for current_link in current_links:
    a_element1 = current_link.find('a')
    title = current_link.find('div',class_='issue-item__title').find('h3').get_text(strip=True)
    DOI = current_link.find('div', class_='issue-item__doi').find('a').getText(strip=True)
    Volume_Issue = soup.find('h2', class_='toc__title').text.strip()[:20]
    issues_date = current_link.find('div', class_='issue-item__header').find_all('span')[1].text.strip()
    encode_Journal_link = 'https://journals.asm.org' + a_element1.get("href")+'?download=true'
    print(title)
    print(issues_date)
    print(Volume_Issue)
    print(DOI)
    print(encode_Journal_link)
    # response = scraper.get(encode_Journal_link, headers=headers)
    #
    # # Check if the request was successful
    # if response.status_code == 200:
    #     output_file_name = ret_file_name_full(title, '.pdf')
    #     with open(output_file_name, 'wb') as pdf_file:
    #         pdf_file.write(response.content)
    #     print(f"Downloaded: {output_file_name}")
    # else:
    #     print(f"Error: Unable to fetch the PDF. Status code: {response.status_code}")