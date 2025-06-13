import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import os
import re
import common_function
from datetime import datetime
import pandas as pd
import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pandas as pd
import chromedriver_autoinstaller as chromedriver

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'ASP.NET_SessionId=jevehm10odtwgpeabekmo42w',
    'Host': 'gdnykx.cnjournals.org',
    'Referer': 'https://gdnykx.cnjournals.org/gdnykxen/ch/reader/issue_browser.aspx',
    'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}
pdf_headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
def get_soup(url,API_KEY):
    scraperapi_url = f"http://api.scraperapi.com/?api_key={API_KEY}&url={url}"
    response = requests.get(scraperapi_url)
    # response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

def get_driver_content(url):
    driver.get(url)
    content = driver.page_source
    cookies = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in driver.get_cookies()])
    soup = BeautifulSoup(content, 'html.parser')
    return soup, cookies

def return_api_key():
    try:
        with open('API_KEY.txt','r') as file:
            content=file.read().strip()
            return content
    except Exception as e:
        error_list.append(e)
        print(e)
API_KEY = return_api_key()
try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

Total_count=None
attachment=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
current_datetime = datetime.now()
current_date = str(current_datetime.date())
current_time = current_datetime.strftime("%H:%M:%S")

ini_path= os.path.join(os.getcwd(),"REF_95.ini")
Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
duplicate_list = []
error_list = []
completed_list=[]
data = []
pdf_count = 1
Ref_value="95"
url_id='950467809'
current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
out_excel_file=common_function.output_excel_name(current_out)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1400,600")
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
url="https://gdnykx.cnjournals.org/gdnykxen/ch/reader/issue_browser.aspx"
try:
    soup = get_soup(url,API_KEY)
    current_issues =soup.find("ul",class_="et_gkll").find_all('li')[-1]
    for current_issue in current_issues:
        Article_link = None
        try:
            Article_link = "https://gdnykx.cnjournals.org/gdnykxen/ch/reader/"+current_issue.get("href")
            current_soup=get_soup(Article_link,API_KEY)
            # current_soup, cookies = get_driver_content(Article_link)
            text =current_soup.find("table",id="table3").find("p").get_text(strip=True)
            pattern = r"Volume (\d+),Issue (\d+),(\d{4})"
            match = re.search(pattern, text)
            if match:
                volume = match.group(1)
                issue = match.group(2)
                year = match.group(3)
                All_Articles = current_soup.find_all("table", id="table24")
                for i,articles in enumerate(All_Articles):
                    if i>1:
                        tr_element=articles.find_all("tr")
                        ele_len=len(tr_element)//4
                        for j in range(ele_len):
                            Article_title=tr_element[1+j*4].text.strip()
                            Article_link1="https://gdnykx.cnjournals.org/gdnykxen/ch/reader/"+tr_element[1+j*4].find('a').get("href")
                            text = tr_element[3 + j * 4].text.strip()
                            pattern = r'(\d+-\d+)'
                            match = re.search(pattern, text)
                            if match:
                                page_range = match.group(1)
                            # current_soup1, cookies = get_driver_content(Article_link1)
                            current_soup1 = get_soup(Article_link1, API_KEY)
                            doi=current_soup1.find('span',id="DOI").text.strip()
                            pdf_link="https://gdnykx.cnjournals.org/gdnykxen/ch/reader/"+current_soup1.find('span',id="URL").find('a').get("href")
                            check_value,tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
                            if Check_duplicate.lower() == "true" and check_value:
                                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                                duplicate_list.append(message)
                                print("Duplicate Article :", Article_title)
                            else:
                                print("Original Article :", Article_title)
                                pdf_content = response = requests.get(pdf_link)
                                output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                with open(output_fimeName, 'wb') as f:
                                    f.write(pdf_content.content)
                                print("PDF downloaded successfully:",output_fimeName)
                                data.append(
                                    {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                                     "Volume": volume, "Issue": issue, "Supplement": "", "Part": "", "Special Issue": "", "Page Range": "",
                                     "Month": "", "Day": "", "Year": year,
                                     "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                                df = pd.DataFrame(data)
                                df.to_excel(out_excel_file, index=False)
                                pdf_count += 1
                                scrape_message = f"{Article_link}"
                                completed_list.append(scrape_message)
                                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                    write_file.write(Article_link + '\n')
        except Exception as error:
            message = f"Error link - {Article_link} : {str(error)}"
            error_list.append(message)
            print(error)

    try:
        common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),str(len(duplicate_list)), str(len(error_list)))
    except Exception as error:
        message = str(error)
        error_list.append(message)
    if str(Email_Sent).lower() == "true":
        attachment_path = out_excel_file
        if os.path.isfile(attachment_path):
            attachment = attachment_path
        else:
            attachment = None
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass
    driver.quit()
except ValueError as API_KEY_expired:
    print(str(API_KEY_expired))
    error_list.append(API_KEY_expired)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
except Exception as error:
    Error_message = "Error in the site :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path,attachment, current_date, current_time, Ref_value)

finally:
    subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
    error_file_path = os.path.join(current_out, 'download_details.html')
    with open(error_file_path, 'w', encoding='utf-8') as file:
        file.write(error_html_content)
    print("Error details file saved to:", error_file_path)
