import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import common_function

source_id = "78155699"

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

try:
    # url = "https://zrzh.paperonce.org/api/api/Web/LastIssueList?_t=1738924325&PageSize=10&PageIndex=0&IssueId=-1"
    url = "https://zrzh.paperonce.org/api/api/Web/LastIssueList?_t=1739163483&PageSize=0&IssueId=0"
    toc_url = "https://zrzh.paperonce.org/en/#/"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_557.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "557"
    print(source_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = get_response_with_retry(url, headers)
    if response.status_code == 200:
        json_data = response.json()

        for article in json_data.get("Data", []):
            article_link, article_title = None, None
            try:
                article_title = article.get("TitleE", "N/A")
                Total_count = len(article_title)
                doi = article.get("DOI", "N/A")
                page_range = f"{article.get('Page_Num', 'N/A')}-{article.get('Page_NumEnd', 'N/A')}"
                pdf_id = article.get("PDFFileNameUrlGUID", "N/A")
                year = article.get("PublishYear", "N/A")
                issue = article.get("IssueNumE", "N/A")
                volume = article.get("Volume", "N/A")
                article_link = article.get("HtmlFileUrl", "N/A")
                pdf_link = f"https://zrzh.paperonce.org/api/api/Web/OpenArticleFilebyGuidNew?Id={pdf_id}"

                check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article:", article_title)

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
                         "user_id": user_id, "TOC File Name": f"{source_id}_TOC.html"})
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
            try:
                response_en = get_response_with_retry(toc_url, headers=headers)
                response_en.raise_for_status()
                soup_en = BeautifulSoup(response_en.text, 'html.parser')

                english_heading = "<h1>Table of Contents - English Version</h1>\n"
                english_content = soup_en.prettify()

            except Exception as e:
                error_message = f"Error processing English version of URL {toc_url}: {str(e)}"
                error_list.append(error_message)
                print(error_message)
                english_heading = "<h1>Error loading English version</h1>\n"
                english_content = f"<p>{error_message}</p>\n"

            try:
                url_cn = toc_url.replace('/en/#/', '/#/')

                response_cn = get_response_with_retry(url_cn, headers=headers)
                response_cn.raise_for_status()
                soup_cn = BeautifulSoup(response_cn.text, 'html.parser')

                chinese_heading = "<h1>Table of Contents - Chinese Version</h1>\n"
                chinese_content = soup_cn.prettify()

            except Exception as e:
                error_message = f"Error processing Chinese version of URL {toc_url}: {str(e)}"
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
            print(f"Error in creating the TOC file: {e}")
            error_list.append(f"Error in creating the TOC file: {e}")

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

except Exception as error:
    Error_message = "Error in processing JSON URL: " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
