import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
import pdfkit
from PyPDF2 import PdfMerger
import common_function
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

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
            base_url = "https://sioc-journal.cn/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_211.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "211"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(response.text, "html.parser")

                div_element = soup.find("div", class_="col-md-12").findAll("div", class_="col-md-6")

                Total_count = len(div_element)
                # print(f"Total number of articles: {Total_count}", "\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("div", class_="j-title")
                        if article_title_div:
                            article_title = article_title_div.find("a").text.strip()
                            article_link = article_title_div.find("a").get('href')

                            pages_range_doi_tag = single_element.find("div", class_="abs_njq")
                            page_range = ""
                            if pages_range_doi_tag:
                                pages_text = pages_range_doi_tag.text
                                page_range_match = re.search(r'\bpp (\d+-\d+)\b', pages_text)
                                if page_range_match:
                                    page_range = page_range_match.group(1)

                                doi_tag = pages_range_doi_tag.find("a")
                                doi = ""
                                if doi_tag:
                                    doi = doi_tag.text.strip()

                                onclick_attr = single_element.find("a", string="PDF")
                                if onclick_attr:
                                    onclick_text = str(onclick_attr)
                                    id_match = re.search(r"lsdy1\('PDF','(\d+)'", onclick_attr['onclick'])
                                    pdf_id = ""
                                    if id_match:
                                        pdf_id = id_match.group(1)

                                    if url == 'https://sioc-journal.cn/Jwk_yjhx/EN/0253-2786/current.shtml':
                                        base_pdf_url = f'https://sioc-journal.cn/Jwk_yjhx/EN/article/downloadArticleFile.do?attachType=PDF&id={pdf_id}'
                                    elif url == 'https://sioc-journal.cn/Jwk_hxxb/EN/0567-7351/current.shtml':
                                        base_pdf_url = f'https://sioc-journal.cn/Jwk_hxxb/EN/article/downloadArticleFile.do?attachType=PDF&id={pdf_id}'
                                    else:
                                        base_pdf_url = ""

                                    if base_pdf_url:
                                        pdf_link = base_pdf_url
                                    else:
                                        print(f"No valid base URL for source_id {source_id}")

                                volume_issue_info = soup.find("p", class_="n-j-q")
                                volume, issue = "", ""
                                if volume_issue_info:
                                    volume_issue_text = volume_issue_info.text.strip()
                                    volume_issue_match = re.search(r'(\d+), (\d+)\((\d+)\)', volume_issue_text)
                                    if volume_issue_match:
                                        year = volume_issue_match.group(1)
                                        volume = volume_issue_match.group(2)
                                        issue = volume_issue_match.group(3)

                                day_month_year_info = soup.find("p", class_="chubanriqi")
                                day, month, year = "", "", ""
                                if day_month_year_info:
                                    day_month_year_text = day_month_year_info.text.strip()
                                    day_month_year_match = re.search(r'(\d+) (\w+) (\d{4})', day_month_year_text)
                                    if day_month_year_match:
                                        day = day_month_year_match.group(1)
                                        month = day_month_year_match.group(2)
                                        year = day_month_year_match.group(3)

                                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id,
                                                                                              volume, issue)
                                        if Check_duplicate.lower() == "true" and check_value:
                                            message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                            duplicate_list.append(message)
                                            print("Duplicate Article :", article_title)
                                        else:
                                            for attempt in range(3):
                                                try:
                                                    pdf_content = http.get(pdf_link, headers=headers, timeout=30).content
                                                    break
                                                except requests.exceptions.RequestException as e:
                                                    if attempt < 2:
                                                        print(f"Retry {attempt + 1} for PDF download: {pdf_link}")
                                                    else:
                                                        raise e

                                            output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                                            with open(output_fileName, 'wb') as file:
                                                file.write(pdf_content)
                                            data.append(
                                                {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                                 "Identifier": "",
                                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                 "Special Issue": "",
                                                 "Page Range": page_range, "Month": month, "Day": day, "Year": year,
                                                 "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                                 "user_id": user_id, "TOC File Name": f"{source_id}_TOC.html"})
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

                try:
                    try:
                        response_en = requests.get(url)
                        response_en.raise_for_status()
                        soup_en = BeautifulSoup(response_en.text, 'html.parser')

                        english_heading = "<h1>Table of Contents - English Version</h1>\n"
                        english_content = soup_en.prettify()

                    except Exception as e:
                        error_message = f"Error processing English version of URL {url}: {str(e)}"
                        error_list.append(error_message)
                        print(error_message)
                        english_heading = "<h1>Error loading English version</h1>\n"
                        english_content = f"<p>{error_message}</p>\n"

                    try:
                        url_ja = url.replace('/EN', '/CN')

                        response_ja = requests.get(url_ja)
                        response_ja.raise_for_status()
                        soup_ja = BeautifulSoup(response_ja.text, 'html.parser')

                        chinese_heading = "<h1>Table of Contents - Chinese Version</h1>\n"
                        chinese_content = soup_ja.prettify()

                    except Exception as e:
                        error_message = f"Error processing Chinese version of URL {url}: {str(e)}"
                        error_list.append(error_message)
                        print(error_message)
                        chinese_heading = "<h1>Error loading Chinese version</h1>\n"
                        chinese_content = f"<p>{error_message}</p>\n"

                    combined_content = f"{english_heading}{english_content}<hr>{chinese_heading}{chinese_content}"

                    output_file = os.path.join(current_out, f"{source_id}_TOC.html")
                    with open(output_file, 'w', encoding='utf-8') as file:
                        file.write(combined_content)

                    print(f"Combined file saved: {output_file}")

                except Exception as e:
                    print(f"Error in creating the TOC file : {e}")
                    error_list.append(f"Error in creating the TOC file : {e}")

                try:
                    common_function.sendCountAsPost(source_id, Ref_value, str(Total_count), str(len(completed_list)),
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
                        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
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
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except Exception as error:
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
