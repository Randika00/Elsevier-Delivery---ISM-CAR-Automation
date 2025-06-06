import os
import re
import time

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import common_function
import pandas as pd
import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver
import random

def first_drive(url,request_cookies):
    driver.get(url)
    content = driver.page_source
    uc_soup = BeautifulSoup(content, 'html.parser')
    return uc_soup

def use_drive(url,request_cookies):
    driver.get(url)
    for cookie_name, cookie_value in request_cookies.items():
        driver.add_cookie({"name": cookie_name, "value": cookie_value})

    driver.get(url)
    content = driver.page_source
    uc_soup = BeautifulSoup(content, 'html.parser')
    return uc_soup

def get_pdf_link(pdf_link):
    driver.get(pdf_link)
    time.sleep(2)
    for i in range(30):
        current_url = driver.current_url
        if current_url != pdf_link:
            return current_url
        time.sleep(1)

request_cookies = {
    'IWA_PublishingMachineID': '638491186796925668',
    '_ga': 'GA1.2.892686197.1713521884',
    '_gid': 'GA1.2.1313269268.1713521884',
    'fpestid': 'eh9u8XUlgdwuY7RUwBCYJv4NZVGOKeP548CWt1y_bFcLNWRt7tUehqHRQCwwsjI1bzLnNw',
    '_cc_id': 'c98eea9794bffe9e84dcd4916e261382',
    'panoramaId_expiry': '1714126683937',
    'panoramaId': '87bb27088c11dbcbf1612371515e16d53938c438922298f84a6f843eb4291467',
    'panoramaIdType': 'panoIndiv',
    'hum_iwap_visitor': '98fc3c8c-f2ea-4750-8fe8-42302f336a62',
    '__stripe_mid': 'debea6e4-2d7d-4d84-aeb3-37410dc7dbe192f50c',
    'IWA_SessionId': 'b0y5gtz4zk0y0gh5xrgouqwm',
    '__stripe_sid': 'f79e02a8-ef2f-4a96-9c7b-3381a4c74abd83cdba',
    '_gat_UA-10590794-3': '1',
    '_gat_UA-76340245-2': '1',
    '_ga_CY814T2KFP': 'GS1.2.1713550821.2.1.1713551342.60.0.0'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value="47"
ini_path=None

check = 0
while check < 10:
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--incognito')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={user_agent}')

        driver = uc.Chrome(options=options)

        check = 10
    except:
        if not check < 9:
            message = "Error in the Chrome driver. Please update your Google Chrome version."
            error_list.append(message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
        check += 1

try:
    with open('urlDetails.txt','r',encoding='utf-8') as file:
        url_list=file.read().split('\n')
except Exception as error:
    print(error)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

p, q = 0, 0
while p < len(url_list):
    try:
        url, url_id = url_list[p].split(',')
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        Ref_value = "47"

        if q == 0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        attachment = None
        pdf_count = 1

        try:
            current_soup=first_drive(url,request_cookies)
            preVolume,preIssue=current_soup.find('div',class_='volume-issue__wrap').text.strip().split(', ')
        except:
            current_soup=use_drive(url,request_cookies)
            preVolume,preIssue=current_soup.find('div',class_='volume-issue__wrap').text.strip().split(', ')


        Volume=preVolume.split()[1]
        Issue=preIssue.split()[1]
        Day,Month,Year=current_soup.find('div',class_='ii-pub-date').text.strip().split()

        All_articles=current_soup.find('div',class_='section-container').findAll('div',class_='al-article-item-wrap al-normal')

        Total_count = len(All_articles)

        i, j = 0, 0
        while i < len(All_articles):

            Article_link,Article_title=None,None
            try:
                Article_link='https://iwaponline.com'+All_articles[i].find('h5',class_='item-title').find('a').get('href')
                Article_title = All_articles[i].find('h5',class_='item-title').text.strip()

                try:
                    Article_details=first_drive(Article_link,request_cookies)
                    pdf_link='https://iwaponline.com'+Article_details.find('li',class_='toolbar-item item-pdf').find('a',class_='article-pdfLink').get('href')
                except:
                    Article_details = use_drive(Article_link, request_cookies)
                    pdf_link = 'https://iwaponline.com' + Article_details.find('li',class_='toolbar-item item-pdf').find('a',class_='article-pdfLink').get('href')
                DOI = Article_details.find('div', class_='citation-doi').text.strip().rsplit('doi.org/', 1)[-1]
                Page_range = Article_details.find('div', class_='ww-citation-primary').text.strip().rsplit('): ', 1)[-1].rstrip('.')

                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{pdf_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)

                else:
                    updatedLink=get_pdf_link(pdf_link)
                    pdf_content = requests.get(updatedLink, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": Day,
                         "Year": Year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title)

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                i, j = i + 1, 0
            except Exception as error:
                if j < 4:
                    j += 1
                else:
                    message=f"{Article_link} : 'NoneType' object has no attribute 'text'"
                    print("Download failed :",Article_title)
                    error_list.append(message)
                    i, j = i + 1, 0

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                            str(len(duplicate_list)),
                                            str(len(error_list)))
        except Exception as error:
            message = f"Failed to send post request : {str(error)}"
            error_list.append(message)

        try:
            if str(Email_Sent).lower() == "true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list), ini_path, attachment, current_date,
                                                     current_time, Ref_value)
        except Exception as error:
            message = f"Failed to send email : {str(error)}"
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list,
                                            completed_list,
                                            len(completed_list), url_id, Ref_value, attachment, current_out)
            # error_list.append(message)


        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        p, q = p + 1, 0
    except Exception as error:
        if q < 4:
            q += 1
        else:
            Error_message = "Error in the driver :" + str(error)
            print("Error in the driver or site")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
            p, q = p + 1, 0

driver.close()
driver.quit()






