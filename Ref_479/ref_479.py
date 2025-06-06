import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
import  time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver
chromedriver.install()
import common_function

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

source_id = "328180399"

cookie = {
  "Oxford_AcademicMachineID": "638646440736496662",
  "fpestid": "lrKR77zgd8sbqW0monNsIZuF2ztEVendNJIZ8m62kkEzQ5oZkOdXu9nqe0VVsfdEoiN5wA",
  "_cc_id": "c97b8ec6c52ea8b9dede8a7a3c14dc29",
  "panoramaId_expiry": "1729652082158",
  "panoramaId": "c7ac1339b80f768b6d796043927116d53938d362765100506395e6c80fa62ce3",
  "panoramaIdType": "panoIndiv",
  "preferences": "C004,C003,C001,C002",
  "last_consent": "cd2f2020-d603-4f75-8d61-2cd4c96ffd9b|1729047290496",
  "_gcl_au": "1.1.356105126.1729047291",
  "dmd-tag": "0234be60-8b6a-11ef-b1f0-99242e1a72df",
  "hum_oup_visitor": "9e1be4fc-c470-485b-b583-238e86c66614",
  "hum_oup_synced": "true",
  "SaneID": "YHxomkJdqu2-ebUmTIl",
  "_hjSessionUser_3072445": "eyJpZCI6ImU2Nzg1NjZhLTIxMWEtNTE4OS1iMzU5LTI5OTRmZTNhOTZmOSIsImNyZWF0ZWQiOjE3MjkwNDcyOTI5NjcsImV4aXN0aW5nIjp0cnVlfQ==",
  "_ga": "GA1.2.1939958600.1729047288",
  "TheDonBot": "2D8CDC1F54EEADB0EC0E50BADDCA4B00",
  "OUP_SessionId": "yya0mwxc00mmmq5ueauyn5xh",
  "_gid": "GA1.2.231958414.1729229094",
  "_hjSession_3072445": "eyJpZCI6Ijg4ZTFmYWQwLWI5MmMtNDNmZC05YTgxLWY0ZWJlMWE0ZDNiYyIsImMiOjE3MjkyMjkwOTUxMzgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=",
  "_ga_GLF90ZEMKF": "GS1.1.1729229091.3.0.1729229110.0.0.0",
  "dmd-sid4": "{\"id\":\"5198bee0-8d11-11ef-9218-c158b1a1d81a\",\"timestamp\":1729229098000,\"lastUpdate\":1729229112000}"
}


duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
time_prefix = None
today_date = None
ini_path = None

check = 0
while check < 10:
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

        options = uc.ChromeOptions()
        #options.add_argument('--headless')
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
    except Exception as error:
        if not check < 9:
            message = "Error in the Chrome driver. Please update your Google Chrome version."
            error_list.append(message)
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
        check += 1

def get_response_with_retry(url, headers, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    response = session.get(url, headers=headers, timeout=30)
    return response

try:
    try:
        with open('urlDetails.txt', 'r', encoding='utf-8') as file:
            url_details = file.readlines()
    except Exception as error:
        Error_message = "Error in the urlDetails.txt file :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                             ini_path, attachment, current_date, current_time, Ref_value)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    try:
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
    except FileNotFoundError:
        with open('completed.txt', 'w', encoding='utf-8'):
            with open('completed.txt', 'r', encoding='utf-8') as read_file:
                read_content = read_file.read().split('\n')

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://academic.oup.com"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_479.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "479"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            try:
                current_soup = first_drive(url, cookie)
                link = current_soup.find("nav", class_="navbar-menu").findAll("li", class_="site-menu-item site-menu-lvl-0 at-site-menu-item")[0].find("a").get("href")
            except:
                current_soup = use_drive(url, cookie)
                link = current_soup.find("nav", class_="navbar-menu").findAll("li", class_="site-menu-item site-menu-lvl-0 at-site-menu-item")[0].find("a").get("href")

            # response = get_response_with_retry(url, headers=headers)

            current_link = base_url + link

            #response = get_response_with_retry(current_link, headers=headers)
            try:
                soup = first_drive(current_link, cookie)
                #link = current_soup.find("nav", class_="navbar-menu").findAll("li", class_="site-menu-item site-menu-lvl-0 at-site-menu-item")[0].find("a").get("href")
            except:
                soup = use_drive(current_link, cookie)
                #link = current_soup.find("nav", class_="navbar-menu").findAll("li", class_="site-menu-item site-menu-lvl-0 at-site-menu-item")[0].find("a").get("href")


            if True:
                #html_content = response.text
                #soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="section-container").findAll("div", class_="al-article-item-wrap al-normal")
                Total_count = len(div_element)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h5", class_="customLink item-title")
                        if article_title_div:
                            article_title = article_title_div.find("a", class_="at-articleLink").text.strip()
                            article_links = article_title_div.find("a", class_="at-articleLink").get('href')
                            article_link = urllib.parse.urljoin(base_url, article_links)

                            volume_issue_date_info = soup.find("h1", class_="issue-identifier").find("div", class_="issue-info-pub")
                            volume, issue, month, year = "", "", "", ""
                            if volume_issue_date_info:
                                pattern = re.compile(r"Volume (\d+), Issue (\d+), (\w+) (\d{4})")
                                match = pattern.search(volume_issue_date_info.text.strip())

                                if match:
                                    volume = match.group(1) if volume_issue_date_info else ""
                                    issue = match.group(2) if volume_issue_date_info else ""
                                    month = match.group(3) if volume_issue_date_info else ""
                                    year = match.group(4) if volume_issue_date_info else ""

                            identifier_doi_tag = single_element.find("div", class_="ww-citation-primary")
                            identifier, doi = "", ""
                            if identifier_doi_tag:
                                doi_link_tag = identifier_doi_tag.find("a")
                                if doi_link_tag:
                                    doi = doi_link_tag.get('href').replace("https://doi.org/", "") if doi_link_tag else ""
                                    identifier = doi_link_tag.text.split('/')[-1] if doi_link_tag else ""

                            last_page_text = single_element.find("ul", class_="al-other-resource-links")
                            last_page_link = ""
                            if last_page_text:
                                last_page_links = last_page_text.find("a", class_="viewArticleLink").get('href') if last_page_text else ""
                                last_page_link = urllib.parse.urljoin(base_url, last_page_links)

                                # last_response = get_response_with_retry(last_page_link, headers=headers)
                                try:
                                    last_soup = first_drive(last_page_link, cookie)
                                except:
                                    last_soup = use_drive(last_page_link, cookie)

                                if True:
                                    pdf_url_info = last_soup.find("li", class_="toolbar-item item-pdf js-item-pdf")
                                    pdf_link = ""
                                    if pdf_url_info:
                                        pdf_text = pdf_url_info.find("a", class_="al-link pdf article-pdfLink").get('href') if pdf_url_info else ""
                                        pdf_link = urllib.parse.urljoin(base_url, pdf_text)

                                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                    if Check_duplicate.lower() == "true" and check_value:
                                        message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                        duplicate_list.append(message)
                                        print("Duplicate Article:", article_title)

                                    else:
                                        updatedLink = get_pdf_link(pdf_link)
                                        pdf_content = requests.get(updatedLink, headers=headers).content
                                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                        with open(output_fimeName, 'wb') as file:
                                            file.write(pdf_content)
                                        data.append(
                                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                             "ItemID": "",
                                             "Identifier": identifier,
                                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                             "Special Issue": "", "Page Range": "", "Month": month,
                                             "Day": "",
                                             "Year": year,
                                             "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                             "user_id": user_id})
                                        df = pd.DataFrame(data)
                                        df.to_excel(out_excel_file, index=False)
                                        pdf_count += 1
                                        scrape_message = f"{article_link}"
                                        completed_list.append(scrape_message)
                                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                            write_file.write(article_link + '\n')
                                        print("Original Article:", article_link)

                    except Exception as error:
                        message = f"Error link - {article_title}: {str(error)}"
                        print(f"{article_title}: {str(error)}")
                        error_list.append(message)

                for attempt in range(25):
                    try:
                        common_function.sendCountAsPost(source_id, Ref_value, str(Total_count), str(len(completed_list)),
                                                        str(len(duplicate_list)), str(len(error_list)))
                        break
                    except Exception as error:
                        if attempt == 24:
                            error_list.append(f"Failed to send post request : {str(error)}")

                try:
                    if str(Email_Sent).lower() == "true":
                        attachment_path = out_excel_file
                        if os.path.isfile(attachment_path):
                            attachment = attachment_path
                        else:
                            attachment = None
                        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
                                                             len(completed_list), ini_path, attachment, current_date,
                                                             current_time, Ref_value)
                except Exception as error:
                    message = f"Failed to send email: {str(error)}"
                    error_list.append(message)

                sts_file_path = os.path.join(current_out, 'Completed.sts')
                with open(sts_file_path, 'w') as sts_file:
                    pass

        except Exception as e:
            Error_message = "Error in the site :" + str(e)
            print(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except Exception as error:
    Error_message = "Error in the urlDetails.txt f ile :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)