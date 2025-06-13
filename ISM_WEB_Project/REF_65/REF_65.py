import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
from datetime import datetime
import pandas as pd
import sys
import os
import common_function

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

ini_path= os.path.join(os.getcwd(),"REF_65.ini")
Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
duplicate_list = []
error_list = []
completed_list=[]
data = []
pdf_count = 1
Ref_value="65"
url_id='644230999'

current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
out_excel_file=common_function.output_excel_name(current_out)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--incognito")

driver = None

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
if driver is None:
    print("Driver initiation failed. Errors:")
else:
    print("Driver initiation success. Success:")

url = 'https://www.sciengine.com/CSB/issue?slug=browse&abbreviated=scp'
try:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    active_dropdown = soup.find('div', class_='tabBox').find_all('div', class_='tab menu-dropdown')[1]
    # if active_dropdown:
    dropdown_items = active_dropdown.find_all('a', class_='childA')[1].get("href")
    all_issues_href = 'https://www.sciengine.com' + dropdown_items
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    driver.get(all_issues_href)
    page_content = driver.page_source
    all_issues_soup = BeautifulSoup(page_content, 'html.parser')
    volume_issue=all_issues_soup.find('div',class_='volumnList')
    volume_text = volume_issue.find('div', class_='volume').text.strip().rsplit('Vol.', 1)[-1]
    issue_lists = volume_issue.find('div', class_='issue')
    issue_number = issue_lists.find('a', class_='lssueText').text.strip().rsplit('No.', 1)[-1]
    content_href=f"https://www.sciengine.com/restData/selectArticlesByJournalIdAndVolumeIssueCodeBySortFlag?journalBaseId=tJmzTo54emWeubAbY&volume={volume_text}&code={issue_number}&isLatest=0"
    response = requests.get(content_href)
    content_data = json.loads(response.text)
    Total_count = len(content_data)
    print(f"Total number of articles:{Total_count}", "\n")
    for i,entry in enumerate(content_data):
        try:
            entry_id = entry.get("id")
            title = entry.get("title").replace('<italic>', '').replace('</italic>', '')
            doi = entry.get("doi")
            article_info=entry.get("articleMetaInfoStr")
            info_parts = [part.strip() for part in article_info.split(',')]
            volume = info_parts[0].replace('Volume ', '')
            issue = info_parts[1].replace('Issue ', '')
            year = info_parts[2].split(' ')[-1]
            month = info_parts[2].split(' ')[0]
            page_range = info_parts[3].strip()[6:]
            pdf_link=f"https://www.sciengine.com/doi/pdf/{entry_id}"
            check_value,tpa_id  = common_function.check_duplicate(doi, title, url_id, volume, issue)
            if Check_duplicate.lower() == "true" and check_value:
                message = f"{entry_id} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", title)
            else:
                print("Original Article :", title)
                pdf_content = requests.get(pdf_link).content
                output_file_name = os.path.join(current_out, f"{pdf_count}.pdf")
                with open(output_file_name, 'wb') as file:
                    file.write(pdf_content)
                print(f"Downloaded: {output_file_name}")
                data.append({"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "", "Year": year,
                             "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                pdf_count += 1
                scrape_message = f"{entry_id}"
                completed_list.append(scrape_message)
                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                    write_file.write(entry_id + '\n')
        except Exception as error:
            message = f"Error link - {entry_id } : {str(error)}"
            error_list.append(message)
            print(error)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)
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
except Exception as error:
    Error_message = "Error in the site :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

