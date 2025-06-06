import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
import calendar
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import common_function

source_id = "78823499"

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
            base_url = "https://www.techscience.com/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_105_02.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "105_02"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            link = soup.find("div", class_="qklb").find("li")

            a_tag = link.find("a", class_="outlink")
            link_url = a_tag["href"] if a_tag else None
            volume_match = re.search(r'v(\d+)', link_url)
            volume = volume_match.group(1) if volume_match else None

            year = link.find("div", class_="kd2").text.strip() if link.find("div", class_="kd2") else None

            article_response = requests.get(link_url, headers=headers)
            if article_response.status_code == 200:
                link_soup = BeautifulSoup(article_response.text, 'html.parser')

                issues_div = link_soup.find("div", class_="qklb")
                if issues_div:
                    issue_list = issues_div.find_all("li")
                    if issue_list:
                        latest_issue = issue_list[-1]

                        a_tag = latest_issue.find("a", class_="outlink")
                        current_link = a_tag["href"] if a_tag else None

                        response = get_response_with_retry(current_link, headers=headers)

                        if response.status_code == 200:
                            html_content = response.text
                            soup = BeautifulSoup(html_content, "html.parser")

                            div_element = soup.find("div", id="con_two_1").findAll("li")
                            Total_count = len(div_element)

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

                                        article_response = requests.get(article_link, headers=headers)
                                        if article_response.status_code == 200:
                                            article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                            pdf_url_tag = article_soup.find("div", class_="html-article-content xxjs").find("div", class_="gengduo")
                                            last_page_link = ""
                                            if pdf_url_tag:
                                                pdf_link_tag = pdf_url_tag.findAll("li")[1]
                                                last_page_link = pdf_link_tag.find("a").get("href")

                                            last_response = requests.get(last_page_link, headers=headers)
                                            if last_response.status_code == 200:
                                                last_soup = BeautifulSoup(last_response.text, "html.parser")

                                                pdf_text = last_soup.find("ul", id="pdf-article-tabs").find("li", id="pdfDownloadLinkLi")
                                                pdf_link = ""
                                                if pdf_text:
                                                    pdf_link = pdf_text.find("a", class_="btn btn-primary", id="pdfDownloadLink").get("href")

                                                check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                                if Check_duplicate.lower() == "true" and check_value:
                                                    message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                                    duplicate_list.append(message)
                                                    print("Duplicate Article :", article_title)

                                                else:
                                                    pdf_content = get_response_with_retry(pdf_link, headers=headers).content
                                                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                                    with open(output_fimeName, 'wb') as file:
                                                        file.write(pdf_content)
                                                    data.append(
                                                        {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                         "ItemID": "",
                                                         "Identifier": "",
                                                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                         "Special Issue": "", "Page Range": page_range, "Month": "",
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
                                                    print("Original Article :", article_link)

                                except Exception as error:
                                    message = f"Error link - {article_title}: {str(error)}"
                                    print(f"{article_title}: {str(error)}")
                                    error_list.append(message)

                            for attempt in range(25):
                                try:
                                    common_function.sendCountAsPost(source_id, Ref_value, str(Total_count),
                                                                    str(len(completed_list)),
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
                                    common_function.attachment_for_email(source_id, duplicate_list, error_list,
                                                                         completed_list,
                                                                         len(completed_list), ini_path, attachment,
                                                                         current_date,
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
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)