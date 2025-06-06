import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import urllib.parse
from datetime import datetime
import os
import time
import common_function
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

source_id = "76462999"

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

def fetch_url(url, headers, retries=3, backoff_factor=0.3):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

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
        raise

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
            base_url = "https://jnm.snmjournals.org/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_180.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "180"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = fetch_url(url, headers)
            if not response:
                continue

            link = BeautifulSoup(response.content, "html.parser").find("div", class_="archive-issue-list").findAll("div", class_="highwire-cite-metadata")[0].find("a", class_="hw-issue-meta-data").get("href")
            current_link = urllib.parse.urljoin(base_url, link)
            print(current_link)

            response = fetch_url(current_link, headers)
            if not response:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            div_element = soup.find("div", class_="issue-toc").findAll("ul", class_="toc-section")
            Total_count = len(div_element)
            # print(f"Total number of articles: {Total_count}\n")

            processed_titles = set()

            for single_element in div_element:
                article_link, article_title = None, None
                try:
                    toc_items = single_element.findAll("li", class_="toc-item")
                    for toc_item in toc_items:
                        article_title_element = toc_item.find("a", class_="highwire-cite-linked-title")
                        if article_title_element:
                            article_title = article_title_element.text.strip()
                            if article_title not in processed_titles:
                                processed_titles.add(article_title)
                                article_links = article_title_element.get("href")
                                article_link = urllib.parse.urljoin(base_url, article_links)

                                volume_issue_info = single_element.find("div", class_="highwire-cite-metadata")
                                volume, issue, month, day, year = "", "", "", "", ""

                                if volume_issue_info:
                                    volume = volume_issue_info.find("span", class_="highwire-cite-metadata-volume highwire-cite-metadata").text.strip()
                                    issue = volume_issue_info.find("span", class_="highwire-cite-metadata-issue highwire-cite-metadata").text.strip().replace("(", "").replace(")", "")

                                    month_year_info = volume_issue_info.find("span", class_="highwire-cite-metadata-date highwire-cite-metadata").text.strip()
                                    month, day, year = re.split(r'\s+', month_year_info)
                                    day = day.strip(',')
                                    year = year.strip(',')

                                pages_doi_info = toc_item.find("div", class_="highwire-cite-metadata")
                                page_range, doi = "", ""
                                if pages_doi_info:
                                    page_range_element = pages_doi_info.find("span", class_="highwire-cite-metadata-pages highwire-cite-metadata")
                                    doi_element = pages_doi_info.find("span", class_="highwire-cite-metadata-doi highwire-cite-metadata")
                                    page_range = page_range_element.text.strip().split(";")[0].strip() if page_range_element else "N/A"
                                    doi = doi_element.text.strip().replace("DOI: https://doi.org/", "") if doi_element else ""

                                article_response = fetch_url(article_link, headers)
                                if not article_response:
                                    raise Exception(f"Failed to fetch article URL: {article_link}")

                                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                                pdf_links = article_soup.find("ul", class_="tabs inline panels-ajax-tab").find("li", class_="last").findAll("a", class_="panels-ajax-tab-tab")
                                pdf_url = ""
                                if pdf_links:
                                    last_pdf_link = pdf_links[-1]
                                    pdf_link = last_pdf_link.get("href")
                                    pdf_url = urllib.parse.urljoin(base_url, pdf_link)

                                check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                if Check_duplicate.lower() == "true" and check_value:
                                    message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                    duplicate_list.append(message)
                                    print("Duplicate Article :", article_title)
                                else:
                                    pdf_response = fetch_url(pdf_url, headers)
                                    if not pdf_response:
                                        raise Exception(f"Failed to fetch PDF URL: {pdf_url}")

                                    output_file_name = os.path.join(current_out, f"{pdf_count}.pdf")
                                    with open(output_file_name, 'wb') as file:
                                        file.write(pdf_response.content)

                                    data.append(
                                        {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "", "Special Issue": "",
                                         "Page Range": page_range, "Month": month, "Day": day, "Year": year, "URL": article_link,
                                         "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})

                                    df = pd.DataFrame(data)
                                    df.to_excel(out_excel_file, index=False)
                                    pdf_count += 1

                                    scrape_message = f"{article_link}"
                                    completed_list.append(scrape_message)
                                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                        write_file.write(article_link + '\n')
                                    print("Original Article :", article_link)

                except Exception as error:
                    message = f"Error link - {article_title} : {str(error)}"
                    print(f"{article_title} : {str(error)}")
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
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except Exception as error:
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
