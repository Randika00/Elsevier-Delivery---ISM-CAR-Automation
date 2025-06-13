import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

pdf_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

headers = {
    "Cache-Control": "no-store",
    "Connection": "Keep-Alive",
    "Content-Encoding": "gzip",
    "Content-Length": "21792",
    "Content-Security-Policy": "frame-ancestors 'self' https://omnidoctor.ru/",
    "Content-Type": "text/html; charset=utf-8",
    "Date": "Tue, 19 Mar 2024 11:11:43 GMT",
    "Keep-Alive": "timeout=10, max=10000",
    "Server": "Apache/2.4.6 (CentOS) mpm-itk/2.4.7-04 OpenSSL/1.0.2k-fips PHP/7.4.33",
    "Strict-Transport-Security": "max-age=31536000; preload",
    "Vary": "Accept-Encoding",
    "X-Frame-Options": "SAMEORIGIN, ALLOW-FROM https://omnidoctor.ru/",
    "X-Powered-By": "PHP/7.4.33",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "RODIN_OJSSID=37c3d4131bc86d43f3ea1868ce12fa7d; currentLocale=en_US; cookieShown=true; _gid=GA1.2.760176992.1710845770; _ym_uid=1710845771103195565; _ym_d=1710845771; _ym_isad=2; _ga_Y7V3G4K7P2=GS1.1.1710845769.1.1.1710846550.0.0.0; _ga=GA1.1.400269993.1710845770",
    "Host": "journals.eco-vector.com",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
ini_path = os.path.join(os.getcwd(), "REF_89.ini")
Download_Path, Email_Sent, Check_duplicate = common_function.read_ini_file(ini_path)
pdf_count=1
url_id="000000"
user_id="user"

url = "https://journals.eco-vector.com/ecolgenet/index"
soup = get_soup(url)
h3_text=soup.find("div",id="currentIssueHome").find("h3").get_text(strip=True)
pattern = r"Vol (\d+), No (\d+) \((\d{4})\)"
match = re.match(pattern, h3_text)
if match:
    volume = match.group(1)
    issue = match.group(2)
    year = match.group(3)
current_issues_link=soup.find("div",class_="titleAuthors").find_all('li')[2].find('a').get("href")
current_page = requests.get(current_issues_link, headers=headers)
current_soup = BeautifulSoup(current_page.content, 'html.parser')
all_issues = current_soup.find_all("div", class_=["dark issueArticlesData", "light issueArticlesData"])
for issue in all_issues:
    Article_link = issue.find('a').get("href")
    Article_title = issue.find('a').get_text(strip=True)
    issue_page = requests.get(Article_link, headers=headers)
    issue_soup = BeautifulSoup(issue_page.content, 'html.parser')
    page_range=issue_soup.find("div",class_="titleAuthors").find_all("li")[-5].get_text(strip=True)
    doi=issue_soup.find("div",class_="titleAuthors").find_all("li")[-2].get_text(strip=True).rsplit('doi.org/',1)[-1]
    pdf_page_url=issue_soup.find("div",id="articleFullText").find("a",class_="file").get("href")
    pdf_soup=get_soup(pdf_page_url)
    pdf_link = pdf_soup.find("div", id="pdfDownloadLinkContainer").find("a", class_="action pdf").get("href")
    pdf_content = requests.get(pdf_link, headers=pdf_headers).content
    output_fimeName = common_function.ret_file_name_full(Download_Path, pdf_count, '.pdf', url_id, user_id)
    with open(output_fimeName, 'wb') as file:
        file.write(pdf_content)
    print(f"Downloaded: {output_fimeName}")
    pdf_count += 1


