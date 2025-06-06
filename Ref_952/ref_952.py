import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import common_function

source_id = "79489799"

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

def get_dynamic_content(url, headers):
    session = HTMLSession()
    response = session.get(url, headers=headers)
    response.html.render(timeout=30)
    return response.html.html

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
            base_url = "https://www.sciengine.com"
            article_div = "https://www.sciengine.com/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_952.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "952"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response_html = get_dynamic_content(url, headers)
            soup = BeautifulSoup(response_html, "html.parser")
            link = soup.find("div", class_="jgNavTabs").find("ul", class_="dropdown-menu").find("a", class_="childA").get('href')
            current_link = base_url + link

            response_html = get_dynamic_content(current_link, headers)
            soup = BeautifulSoup(response_html, "html.parser")
            div_element = soup.find("div", class_="listsBox").findAll("div", class_="listBox")
            Total_count = len(div_element)
            print(f"Total number of articles: {Total_count}\n")

            for single_element in div_element:
                article_link, article_title = None, None
                try:
                    article_title_div = single_element.find("div", class_="title")
                    if article_title_div:
                        article_links = article_title_div.find("a").get('href')
                        article_link = urllib.parse.urljoin(article_div, article_links)
                        article_text_span = article_title_div.find("span")
                        if article_text_span:
                            article_title = article_text_span.get_text(separator=" ", strip=True)

                        pages_tag = single_element.find("div", class_="desc")
                        page_range, volume, issue, year = "", "", "", ""
                        if pages_tag:
                            page_text = pages_tag.get_text(strip=True)
                            match = re.search(r"Volume (\d+), Issue (\d+), (\d+), Pages (\d+-\d+)", page_text)

                            if match:
                                volume = match.group(1)
                                issue = match.group(2)
                                year = match.group(3)
                                page_range = match.group(4)
                        else:
                            print("No publication data found!")

                        doi_tag = single_element.find("div", class_="share").find("a", class_="link")
                        doi = ""
                        if doi_tag:
                            doi = doi_tag.get_text(strip=True).replace("https://doi.org/", "") if doi_tag else ""
                        else:
                            print("No do found!")

                        url_tag = single_element.find("div", class_="labelBox").find("span", class_="imgText")
                        pdf_link = ""
                        if url_tag:
                            pdf_tag = url_tag.find("a", class_="pdfLink").get('href')
                            pdf_link = urllib.parse.urljoin(base_url, pdf_tag)

                        else:
                            print("No pdf link found!")

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
                                 "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "",
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
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
