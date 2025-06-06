import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from PyPDF2 import PdfReader
from io import BytesIO
import common_function

source_id = "79655299"

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


def print_first_page_text(pdf_url):
    page_range = "Not Found"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

        response = requests.get(pdf_url, headers=headers, timeout=30)

        if response.status_code == 200:
            pdf_file = BytesIO(response.content)
            pdf_reader = PdfReader(pdf_file)
            first_page = pdf_reader.pages[0]
            first_page_text = first_page.extract_text()

            page_range_match = re.search(r'\b(\d{3,4}-\d{3,4})\b', first_page_text)
            if page_range_match:
                page_range = page_range_match.group(1)
        else:
            print(f"Failed to fetch PDF. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return page_range


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
            base_url = "https://neptjournal.com/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_489.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "489"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            link = soup.find("div", class_="well volumes").findAll("li")[0]

            anchor = link.find("a")
            current_link = anchor['href']
            text = anchor.text.strip()

            pattern = r"Vol (\d+), No (\d+), (\w+) (\d{4})"
            match = re.search(pattern, text)

            volume, issue, month, year = "", "", "", ""
            if match:
                volume = match.group(1)
                issue = match.group(2)
                month_abbr = match.group(3)
                year = match.group(4)

                month = datetime.strptime(month_abbr, "%b").strftime("%B")
            else:
                print("Pattern not found.")

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="col-lg-8").findAll("div", class_="well")

                Total_count = len(div_element)
                # print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h4")
                        if article_title_div:
                            article_title = article_title_div.text.strip()

                            article_link_tag = single_element.find("div", class_="row icons-all").findAll("div", class_="col-md-4 col-6")[2]
                            article_link = ""
                            if article_link_tag:
                                article_link = article_link_tag.find("a").get('href')
                            else:
                                doi = "ARTICLE LINK not found"

                            doi_tag = single_element.find("div", class_="col-md-12")
                            doi = ""
                            if doi_tag:
                                doi = doi_tag.find("a").get('href').replace("https://doi.org/", "")
                            else:
                                doi = "DOI not found"

                            url_text = single_element.find("div", class_="col-md-12")
                            pdf_link = ""
                            if url_text:
                                pdf_link = url_text.find("a").get('href')
                            else:
                                pdf_link = "PDF LINK not found"

                            page_range = ""
                            if pdf_link:
                                page_range = print_first_page_text(pdf_link)

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
                                     "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "",
                                     "Year": year,
                                     "URL": article_link,
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
