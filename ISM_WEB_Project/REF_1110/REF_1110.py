import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd
import chromedriver_autoinstaller as chromedriver
import time
import shutil
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

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

headers = {
    # ":authority": "portlandpress.com",
    # ":method": "GET",
    # ":path": "/clinsci",
    # ":scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

pdf_headers={ "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
              }

chromedriver.install()


def get_token(url):
    response = requests.get(url,headers=headers)
    cookie=response.cookies
    print(cookie)
    token=cookie.get("JSESSIONID").replace("-","")
    return token

def get_soup(url):
    curl = f"http://api.scraperapi.com?api_key=9c5044e75f177a7c90a667bc3123207b&url={url}"
    response = requests.get(curl, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def print_bordered_message(message):
    border_length = len(message) + 4
    border = "-" * (border_length - 2)

    print(f"+{border}+")
    print(f"| {message} |")
    print(f"+{border}+")
    print()

def get_ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

duplicate_list = []
error_list = []
completed_list = []
attachment = None
url_id = None
current_date = None
current_time = None
Ref_value = None
ini_path = None
Total_count = None

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

try:
    with open('urlDetails.txt', 'r', encoding='utf-8') as file:
        url_list = file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\" : " + str(error)
    print_bordered_message(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

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
url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        print_bordered_message("Process started...")
        print("This may take some time. Please wait..........")
        url, url_id = url_list[url_index].split(',')
        print(f"Executing this {url}")

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "REF_1110.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "1110"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1
        url_value = url.split('/')[-3]

        soup = get_soup(url)

        current_issue_link="https://portlandpress.com"+soup.find('div', class_='view-current-issue').find('a',class_="button").get('href')
        current_issue_soup=get_soup(current_issue_link)

        meta_text_issue=current_issue_soup.find('span',class_="volume issue").get_text(strip=True)
        match = re.search(r"Volume\s(\d+),\sIssue\s(\d+)", meta_text_issue)

        if match:
            volume = match.group(1)
            issue = match.group(2)
        else:
            print("Pattern not found")

        meta_text_date = current_issue_soup.find('div', class_="ii-pub-date").get_text(strip=True)
        match = re.search(r"([A-Za-z]+)\s(\d{4})", meta_text_date)

        if match:
            month = match.group(1)
            year = match.group(2)
        else:
            print("No match found.")
        print(f'year="{year}", volume="{volume}", issue="{issue}", month="{month}"')
        All_articles =current_issue_soup.find_all("div",class_="al-article-items")
        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}", "\n")
        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index + 1
            Article_link, Article_title = None, None
            try:
                Article_link = "https://portlandpress.com"+All_articles[article_index].find("h5",class_="customLink item-title").find("a").get('href')
                Article_title = All_articles[article_index].find("h5",class_="customLink item-title").find("a").text.strip()
                page_range_text=All_articles[article_index].find("div",class_="ww-citation-primary").text.strip()
                match = re.search(r"(\d+–\d+)", page_range_text)
                if match:
                    page_range = match.group(1)
                else:
                    print("No match found.")
                doi_html=All_articles[article_index].find("a",class_="al-link pdf openInAnotherWindow stats-item-pdf-download js-download-file-gtm-datalayer-event article-pdfLink")

                if match:
                    doi = doi_html['data-doi']
                else:
                    print("No match found.")
                pdf_link="https://portlandpress.com"+All_articles[article_index].find('a', class_="al-link pdf openInAnotherWindow stats-item-pdf-download js-download-file-gtm-datalayer-event article-pdfLink").get('href')
                print_bordered_message(f"DOI: {doi},pdf_link:{pdf_link}")

                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print_bordered_message(f"Duplicate Article: {Article_title}")
                else:
                    updatedLink = get_pdf_link(pdf_link)
                    pdf_content = requests.get(updatedLink, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    print(output_fimeName)

                data.append(
                        {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                         "Identifier":"",
                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "", "Year": year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                pdf_count += 1
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
                print(get_ordinal_suffix(Article_count)+" article is original article" +"\n"+"Article title:", Article_title,"✅"+ '\n')

                article_index, article_check = article_index + 1, 0
            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"Error link - {Article_link} : {str(error)}"
                    print_bordered_message(f"Download failed: {Article_title}")
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)), str(len(error_list)))
        except Exception as error:
            message = str(error)
            error_list.append(message)

        if str(Email_Sent).lower() == "true":
            attachment_path = out_excel_file
            if os.path.isfile(attachment_path):
                attachment = attachment_path
            else:
                attachment = None
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list, len(completed_list), url_id, Ref_value, attachment, current_out)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the site:" + str(error)
            print_bordered_message(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list, len(completed_list), url_id, Ref_value, attachment, current_out)
            url_index, url_check = url_index + 1, 0
driver.quit()