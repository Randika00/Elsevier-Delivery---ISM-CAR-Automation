import os
import pandas as pd
import requests
import re
import urllib3
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
import certifi
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

url_id = "78397099"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
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

session = requests.Session()
retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

try:
    url = "https://www.techscience.com/cmc/index.html"
    base_url = "https://www.techscience.com/"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_105_03.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "105_03"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = session.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    all_articles = soup.find("div", id="con_two_1").findAll("div", class_="bq2")

    Total_count = len(all_articles)
    # print(f"Total number of articles:{Total_count}", "\n")

    div_element = soup.find("div", id="con_two_1").findAll("li")

    for single_element in div_element:
        article_link, article_title = None, None
        try:
            article_link_tag = single_element.find("div", class_="bq2")
            if article_link_tag:
                article_title = article_link_tag.find("a", class_="h3").text.strip()
                article_link = article_link_tag.find("a", class_="h3").get("href")

                volume_issue_info = single_element.find("div", class_="bq2").find("p").text.strip()

                match = re.search(r'Vol\.(\d+), No\.(\d+)', volume_issue_info)
                volume, issue = "", ""
                if match:
                    volume = match.group(1)
                    issue = match.group(2)

                pages_year_info = single_element.find("div", class_="bq2").find("p").text.strip()

                match_pages_year = re.search(r'pp\.\s*(\d+-\d+),\s*(\d{4})', pages_year_info)
                page_range, year = "", ""
                if match_pages_year:
                    page_range = match_pages_year.group(1)
                    year = match_pages_year.group(2)

                doi_info = single_element.find("div", class_="bq2").find("p").text.strip()
                doi_match = re.search(r'DOI:(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', doi_info, re.IGNORECASE)
                doi = ""
                if doi_match:
                    doi = doi_match.group(1)

                article_response = session.get(article_link, headers=headers, timeout=10)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                pdf_url_tag = article_soup.find("div", class_="html-article-content xxjs").find("div", class_="gengduo")
                last_page_link = ""
                if pdf_url_tag:
                    pdf_link_tag = pdf_url_tag.findAll("li")[1]
                    last_page_link = pdf_link_tag.find("a").get("href")

                last_response = session.get(last_page_link, headers=headers, timeout=10)
                last_response.raise_for_status()
                last_soup = BeautifulSoup(last_response.text, "html.parser")

                page_url = last_soup.find("div", class_="ncenter").find("ul", class_="ul_Address borDown")
                pdf_url = ""
                if page_url:
                    page_link = page_url.findAll("li", class_="address_like")[0]
                    pdf_url = page_link.find("a").get("href")

                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)

                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print("Duplicate Article :", article_title)
                    else:
                        pdf_content = session.get(pdf_url, headers=headers, timeout=10).content
                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_fimeName, 'wb') as file:
                            file.write(pdf_content)
                        data.append(
                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                             "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "",
                             "Year": year,
                             "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{article_link}"
                        completed_list.append(scrape_message)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(article_link + '\n')
                        print("Original Article :", article_link)

        except requests.exceptions.RequestException as error:
            message = f"Error link - {article_title} : {str(error)}"
            print(f"{article_title} : {str(error)}")
            error_list.append(message)

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
        error_list.append(message)

    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass

except Exception as e:
    Error_message = "Error in the site :" + str(e)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
