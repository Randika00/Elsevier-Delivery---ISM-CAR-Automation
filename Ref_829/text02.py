import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from googletrans import Translator
from datetime import datetime
import os
import common_function
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

translator = Translator()

source_id = "315961499"

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
        Error_message = "Error in the urlDetails.txt file: " + str(error)
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
            pass
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://engstroy.spbstu.ru/en"
            article_link_tag = "https://ejvs.journals.ekb.eg/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_829.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "829"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            current_link = BeautifulSoup(response.content, "html.parser").find("div", class_="j-issue").find("div", class_="j-image").find("a", class_="image").get("href")

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="col-md-8 col-md-pull-4").findAll("div", class_="article-item")

                Total_count = len(div_element)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_title_div = single_element.find("h2", class_="article-item-heading")
                    if article_title_div:
                        article_title = article_title_div.find("a").text.strip()
                        article_link = article_title_div.find("a").get('href')

                        match = re.search(r'\.(\d+)/?$', article_link)
                        article_id = ""
                        if match:
                            article_id = match.group(1)
                            article_id = article_id.zfill(2)
                        else:
                            print("Article ID not found")

                        pages_text = single_element.find("ul", class_="article-item-data").findAll("li")[2]
                        page_range = ""
                        if pages_text:
                            page_range = pages_text.text.strip().replace("Pages:", "") if pages_text else ""

                        year_volume_issue_info = soup.find("div", class_="j-contents-info").findAll("span", class_="j-count")
                        volume, issue, year = "", "", ""
                        if year_volume_issue_info:
                            year = year_volume_issue_info[0].get_text(strip=True).split("Year:")[-1].strip() if year_volume_issue_info else ""
                            volume = year_volume_issue_info[1].get_text(strip=True).split("Volume:")[-1].strip() if year_volume_issue_info else ""
                            issue = year_volume_issue_info[2].get_text(strip=True).split("Issue:")[-1].strip() if year_volume_issue_info else ""

                            article_response = get_response_with_retry(article_link, headers=headers)
                            if article_response.status_code == 200:
                                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                doi_tags = article_soup.find("div", class_="article-data").findAll("span", class_="article-data-desc")
                                doi = ""
                                if doi_tags:
                                    doi = doi_tags[1].text.strip() if doi_tags else ""
                                else:
                                    print("DOI not found")















        except Exception as e:
            Error_message = "Error in the site: " + str(e)
            print(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except Exception as error:
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)