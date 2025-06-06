import os
import pandas as pd
import requests
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime
import common_function
from time import sleep
from requests.exceptions import RequestException, ConnectionError, Timeout, HTTPError

duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
source_id = None
time_prefix = None
today_date = None
ini_path = None

MAX_RETRIES = 3
RETRY_BACKOFF = 2

def fetch_with_retries(url, headers, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=(10, 30))
            response.raise_for_status()
            return response
        except (ConnectionError, Timeout) as e:
            if attempt < max_retries - 1:
                sleep(RETRY_BACKOFF ** attempt)
            else:
                raise
        except HTTPError as e:
            raise

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
            pass
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_22.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "22"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = fetch_with_retries(url, headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", id="current-issue").findAll("div", class_="article")

                Total_count = len(div_element)
                print(f"Total number of articles: {Total_count}", "\n")

                printed_titles = set()

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_element = single_element.find("h5", class_="title")
                        if article_title_element:
                            article_title = article_title_element.text.strip()
                            if article_title not in printed_titles:
                                printed_titles.add(article_title)

                        if single_element.a:
                            relative_url = single_element.a.get('href')
                            if relative_url:
                                article_link = urljoin(url, relative_url)

                                page_span = single_element.find_next('span', class_='pages')
                                page_range = ""
                                if page_span:
                                    page_range = page_span.text.strip().replace("Pages:", "") if page_span else ""

                                    p_element = soup.find("p", class_="date-published")
                                    volume_issue_text = p_element.find_all("a")[0].text.strip()

                                    match = re.search(r'Vol (\d+), No (\d+) \((\w+), (\d+)\)', volume_issue_text)
                                    volume, issue, month, year = "", "", "", ""
                                    if match:
                                        volume, issue, month, year = match.groups() if match else ""

                                    article_response = fetch_with_retries(article_link, headers)
                                    if article_response.status_code == 200:
                                        article_soup = BeautifulSoup(article_response.content, 'html.parser')
                                        doi_tag = article_soup.find('p', class_='doi')
                                        doi = ""
                                        if doi_tag:
                                            doi = doi_tag.text.strip().replace("doi:", "") if doi_tag else ""

                                        breadcrumb_tag = article_soup.find('div', id='breadcrumb')
                                        day = ""
                                        if breadcrumb_tag:
                                            breadcrumb_text = breadcrumb_tag.get_text()
                                            day_match = re.search(r'(\d+), ' + year, breadcrumb_text)
                                            if day_match:
                                                day = day_match.group(1) if day_match else ""

                                        last_page_link = single_element.find('a', href=lambda href: (href and "pdf" in href)).get('href')

                                        last_response = fetch_with_retries(last_page_link, headers)
                                        last_soup = BeautifulSoup(last_response.text, "html.parser")

                                        pdf_link = last_soup.find("li", id="pdfDownloadLinkLi").find("a", class_="btn btn-primary").get('href')

                                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)
                                        if Check_duplicate.lower() == "true" and check_value:
                                            message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                            duplicate_list.append(message)
                                            print("Duplicate Article:", article_title)

                                        else:
                                            pdf_content = fetch_with_retries(pdf_link, headers).content
                                            output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                            with open(output_fimeName, 'wb') as file:
                                                file.write(pdf_content)
                                            data.append(
                                                {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                 "ItemID": "",
                                                 "Identifier": "",
                                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                 "Special Issue": "", "Page Range": page_range, "Month": month,
                                                 "Day": day,
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

                try:
                    common_function.sendCountAsPost(source_id, Ref_value, str(Total_count), str(len(completed_list)),
                                                    str(len(duplicate_list)),
                                                    str(len(error_list)))
                except Exception as error:
                    message = f"Failed to send post request: {str(error)}"
                    error_list.append(message)

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
