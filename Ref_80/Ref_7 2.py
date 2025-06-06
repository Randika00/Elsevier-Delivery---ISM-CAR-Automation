import time

import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd
import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver

chromedriver.install()

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
options.add_argument('--user-agent=YOUR_USER_AGENT_STRING')
options.add_argument('--version_main=108')

driver = uc.Chrome(options=options)

request_cookies={
    'American_Association_of_ImmunologistsMachineID': '638471601269158797',
    'fpestid': 'uj4xHuJZCmsEO4iwaCml_ZkpQFn5g5saJ4PWcjuRSSLLuOlaM_8XgtiSo8KUh7FqKXfODQ',
    '_ga': 'GA1.1.1738412850.1711563329',
    '_cc_id': '23c309b2b916c241c5354943d7a590ab',
    'panoramaId_expiry': '1712168129750',
    'panoramaId': 'f172d411e6629317a72b7b3d0265185ca02cd0398a246c61e4507a03ae330588',
    'panoramaIdType': 'panoDevice',
    '__gpi': 'UID=00000d6e75e9420f:T=1711563329:RT=1711569659:S=ALNI_MYnqJqt7ok2paUm1nGOX71B0ZffsQ',
    'TheDonBot': '93CD1E864CFC6333E47A0976D607D384',
    '_ga_G5TCNFJCYP': 'GS1.1.1711734015.2.0.1711734015.0.0.0',
    'AAI_SessionId': 'epl2u5ihy1zrrzyar0bq0w4f',
    '__gads': 'ID=6fda084ce091ab7e:T=1711563329:RT=1711946941:S=ALNI_Ma1p7ggsV0Uk_PmHTTPGLWi9m1M0w',
    '__eoi': 'ID=d4f6ab1a31868add:T=1711563329:RT=1711946941:S=AA-AfjZwpT1cyKFeLlJ7WwhSyOfC',
    'GDPR_54_journals.aai.org': 'true',
    '_ga_333EE1C4XR': 'GS1.1.1711946940.7.1.1711946990.0.0.0'
}

def use_drive(url,request_cookies):
    driver.get(url)
    time.sleep(2)
    driver.get(url)
    for cookie_name, cookie_value in request_cookies.items():
        driver.add_cookie({"name": cookie_name, "value": cookie_value})

    driver.get(url)
    content = driver.page_source
    uc_soup = BeautifulSoup(content, 'html.parser')
    return uc_soup

def get_cookies():
    cookies = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in driver.get_cookies()])
    return cookies

duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None

try:
    with open('urlDetails.txt','r',encoding='utf-8') as file:
        url_list=file.read().split('\n')
except Exception as error:
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

for i,url_url_id in enumerate(url_list):
    try:
        url,url_id=url_url_id.split(',')
        data = []
        duplicate_list = []
        error_list = []
        completed_list=[]
        pdf_count=1

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "Info.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        Ref_value = "7"
        print(url_id)

        uc_soup = use_drive(url,request_cookies)
        soup = uc_soup.find('div', class_='article-issue-info')
        Volume = re.sub(r'[^0-9]+', "", soup.find('div', class_='volume').text.strip())
        Issue = re.sub(r'[^0-9]+', "", soup.find('div', class_='issue').text.strip())
        Date,Month,Year = soup.find('div', class_='ii-pub-date').text.strip().split(' ')
        All_articles = use_drive("https://journals.aai.org/" + soup.find('div', class_='view-current-issue').find('a').get('href'),request_cookies).find('div',class_='section-container').findAll('div', class_='al-article-item-wrap al-normal')
        for sin_art in All_articles:
            Article_link,Article_title=None,None
            try:
                Article_title = sin_art.find('h5', class_='item-title').find('a').text.strip()
                Article_link="https://journals.aai.org" + sin_art.find('h5', class_='item-title').find('a').get('href')
                if not Article_link in read_content:
                    Page_range = sin_art.find('div', class_='ww-citation-primary').text.strip().rsplit('): ', 1)[-1].rstrip('.')
                    Article_details = use_drive(
                        "https://journals.aai.org" + sin_art.find('h5', class_='item-title').find('a').get('href'),request_cookies)
                    pdf_link_check=Article_details.find('ul',class_='debug js-toolbar toolbar')
                    pdf_link='https://journals.aai.org'+pdf_link_check.find('li', class_='item-pdf').find('a').get('href')
                    DOI = Article_details.find('div', class_='ww-citation-wrap-doi').find('a').text.strip().rsplit(
                        'doi.org/', 1)[-1].rstrip('.')
                    check_value = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{Article_link} - duplicate record with TPAID {{tpaid returned in response}}"
                        duplicate_list.append(message)
                        print("Duplicate Article :", Article_title)

                    else:
                        cookies=get_cookies()
                        headers = {
                            "Cookie": f"{cookies}",
                            #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                            'User-Agent': 'YOUR_USER_AGENT_STRING'
                        }
                        #get_driver_pdf(pdf_link, pdf_save, download_path,request_cookies)
                        pdf_content = requests.get(pdf_link, headers=headers).content
                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_fimeName, 'wb') as file:
                            file.write(pdf_content)
                        data.append(
                            {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": "", "Year": Year,
                             "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_link + '\n')
                        print("Original Article :", Article_title)
                else:
                    print("Already downloaded article :", Article_title)
            except Exception as error:
                message=f"Error link - {Article_link} : {str(error)}"
                print(f"{Article_title} : {str(error)}")
                error_list.append(message)

        if str(Email_Sent).lower() == "true":
            attachment_path = out_excel_file
            if os.path.isfile(attachment_path):
                attachment = attachment_path
            else:
                attachment = None
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list), ini_path, attachment, current_date,
                                                 current_time, Ref_value)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
    except Exception as error:
        Error_message = "Error in the site :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                             ini_path, attachment, current_date, current_time, Ref_value)

driver.quit()






