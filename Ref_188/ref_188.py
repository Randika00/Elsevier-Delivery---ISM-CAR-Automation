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

source_id = "77888499"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

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
time_prefix = None
today_date = None
ini_path = None

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        pass
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')

try:
    base_url = "https://jeit.ac.cn/"
    EN_url = "https://jeit.ac.cn/en/article/current"
    CN_url = "https://jeit.ac.cn/article/current"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_188.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "188"
    print(source_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response_en = http.get(EN_url, headers=headers, timeout=30)
    soup_en = BeautifulSoup(response_en.text, 'html.parser')
    response_cn = http.get(CN_url, headers=headers, timeout=30)
    soup_cn = BeautifulSoup(response_cn.text, 'html.parser')

    div_elements_en = soup_en.find("div", class_="articleListBox active base-catalog").findAll("div", class_="article-list")

    Total_count = len(div_elements_en)
    # print(f"Total number of articles:{Total_count}", "\n")

    for single_element in div_elements_en:
        article_link, article_title = None, None
        try:
            article_title_div = single_element.find("div", class_="article-list-title")
            if article_title_div:
                article_title = article_title_div.find("a").text.strip() if article_title_div else ""

                article_text = article_title_div.find("a").get("href") if article_title_div else ""
                article_link = "https:" + article_text

                page_range_info = single_element.find("div", class_="article-list-time")
                page_range = ""
                if page_range_info:
                    info_text = page_range_info.find("font").text.strip()
                    match = re.search(r"(\d{4}),\s+(\d+)\((\d+)\):\s+([\d-]+)", info_text)
                    if match:
                        page_range = match.group(4)

                    volume_issue_year_info = soup_en.find("h2", class_="journalIssue text-center commontit")
                    volume, issue, year = "", "", ""
                    if volume_issue_year_info:
                        info_text = volume_issue_year_info.find("p").text.strip()
                        match = re.search(r"(\d{4}),\s+Volume\s+(\d+),\s+Issue\s+(\d+)", info_text)
                        if match:
                            year = match.group(1)
                            volume = match.group(2)
                            issue = match.group(3)

                    doi = ""
                    doi_tag = single_element.find("div", class_="article-list-time")
                    if doi_tag:
                        doi_link = doi_tag.find("a")
                        if doi_link:
                            doi = doi_link.get("href").replace("http://dx.doi.org/", "")
                        else:
                            doi = ""

                    pdf_id_tags = single_element.find("div", class_="box")
                    id_value = ""
                    if pdf_id_tags:
                        font_tag = pdf_id_tags.find("font", class_="font3")
                        if font_tag:
                            onclick_text = font_tag.find("a").get("onclick")
                            match = re.search(r"downloadpdf\('([^']+)'\)", onclick_text)
                            if match:
                                id_value = match.group(1)

                        pdf_url = f'https://jeit.ac.cn/article/exportPdf?id={id_value}&language=en'

                        article_response = requests.get(article_link, headers=headers)
                        if article_response.status_code == 200:
                            article_soup = BeautifulSoup(article_response.text, 'html.parser')

                            month_info = article_soup.find("div", class_="ii-pub-date")
                            month = ""
                            if month_info:
                                month_text = month_info.text.strip()
                                month = month_text.split()[0]

                            check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                            if Check_duplicate.lower() == "true" and check_value:
                                message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                duplicate_list.append(message)
                                print("Duplicate Article :", article_title)
                            else:
                                for attempt in range(3):
                                    try:
                                        pdf_content = http.get(pdf_url, headers=headers, timeout=30).content
                                        break
                                    except requests.exceptions.RequestException as e:
                                        if attempt < 2:
                                            print(f"Retry {attempt + 1} for PDF download: {pdf_url}")
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
                                     "Page Range": page_range, "Month": month, "Day": "", "Year": year,
                                     "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                     "user_id": user_id, "TOC File Name": f"{source_id}_{volume}_{issue}_TOC.html"})
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
            response_en = requests.get(EN_url)
            response_en.raise_for_status()
            soup_en = BeautifulSoup(response_en.text, 'html.parser')

            english_heading = "<h1>Table of Contents - English Version</h1>\n"
            english_content = soup_en.prettify()

        except Exception as e:
            error_message = f"Error processing English version of URL {EN_url}: {str(e)}"
            error_list.append(error_message)
            print(error_message)
            english_heading = "<h1>Error loading English version</h1>\n"
            english_content = f"<p>{error_message}</p>\n"

        try:
            url_ja = EN_url.replace('/en/article/current', '/article/current')

            response_cn = requests.get(url_ja)
            response_cn.raise_for_status()
            soup_cn = BeautifulSoup(response_cn.text, 'html.parser')

            chinese_heading = "<h1>Table of Contents - Chinese Version</h1>\n"
            chinese_content = soup_cn.prettify()

        except Exception as e:
            error_message = f"Error processing Chinese version of URL {EN_url}: {str(e)}"
            error_list.append(error_message)
            print(error_message)
            chinese_heading = "<h1>Error loading Chinese version</h1>\n"
            chinese_content = f"<p>{error_message}</p>\n"

        combined_content = f"{english_heading}{english_content}<hr>{chinese_heading}{chinese_content}"

        output_file = os.path.join(current_out, f"{source_id}_{volume}_{issue}_TOC.html")
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
    common_function.attachment_for_email(
        source_id, duplicate_list, error_list, completed_list, len(completed_list),
        ini_path, attachment, current_date, current_time, Ref_value
    )

