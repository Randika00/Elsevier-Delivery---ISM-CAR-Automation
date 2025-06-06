import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
from urllib.parse import urljoin
from datetime import datetime
import pdfkit
from PyPDF2 import PdfMerger
import common_function
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys
import logging

url_id = "77876399"

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

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

try:
    try:
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
    except FileNotFoundError:
        with open('completed.txt', 'w', encoding='utf-8'):
            pass
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

    base_url = "https://www.gpxygpfx.com/EN"
    url = "https://www.gpxygpfx.com/EN/volumn/current.shtml"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_266.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "266"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = http.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, "html.parser")

    div_elements = soup.find("td", {"height": "30", "align": "center"}).findAll("table", {"cellspacing": "0", "cellpadding": "0", "width": "100%", "border": "0"})

    Total_count = len(div_elements)
    # print(f"Total number of articles:{Total_count}", "\n")

    processed_titles = set()

    for single_element in div_elements:
        article_link, article_title = None, None
        try:
            article_title_tag = single_element.find("td", {"valign": "center", "align": "left", "colspan": "2", "height": "22"})
            if article_title_tag:
                article_title = article_title_tag.find("b").text.strip()
                if article_title not in processed_titles:
                    processed_titles.add(article_title)

                    article_link_tag = single_element.find("a", string=re.compile("Abstract"))

                    if article_link_tag:
                        relative_link = article_link_tag.get('href').replace("..", "")

                        if not relative_link.startswith('/EN/'):
                            relative_link = '/EN' + relative_link
                        article_link = urljoin(base_url, relative_link)

                        doi_tag = single_element.find_all("tr")[3].find("td", {"align": "left", "colspan": "2", "height": "22", "valign": "middle"})
                        doi = ""
                        if doi_tag:
                            doi_text = doi_tag.get_text(strip=True)
                            doi_match = re.search(r"DOI: (\S+)", doi_text)
                            if doi_match:
                                doi = doi_match.group(1)

                        page_range_tag = single_element.find_all("tr")[4]
                        page_range = ""
                        if page_range_tag:
                            page_range_text = page_range_tag.get_text(strip=True)
                            page_range_match = re.search(r'(\d+-\d+)', page_range_text)
                            if page_range_match:
                                page_range = page_range_match.group(1)

                        onclick_attr = single_element.find("a", string="PDF")
                        if onclick_attr:
                            onclick_text = str(onclick_attr)
                            id_match = re.search(r"lsdy1\('PDF','(\d+)'", onclick_attr['onclick'])
                            pdf_id = ""
                            if id_match:
                                pdf_id = id_match.group(1)

                            base_pdf_url = "https://www.gpxygpfx.com/EN/article/downloadArticleFile.do?attachType=PDF&id="
                            pdf_link = base_pdf_url + str(pdf_id)

                            year_volume_issue_info = soup.find("span", class_="STYLE36")
                            year, volume, issue, month = "", "", "", ""
                            if year_volume_issue_info:
                                year_volume_issue_text = year_volume_issue_info.find("strong").get_text(strip=True)

                                year_match = re.search(r'(\d{4})', year_volume_issue_text)
                                volume_match = re.search(r'Vol\. (\d+)', year_volume_issue_text)
                                issue_match = re.search(r'No\. (\d+)', year_volume_issue_text)
                                month_match = re.search(r'Published: \d{2} (\w+) \d{4}', year_volume_issue_text)

                                year = year_match.group(1) if year_match else ""
                                volume = volume_match.group(1) if volume_match else ""
                                issue = issue_match.group(1) if issue_match else ""
                                month = month_match.group(1) if month_match else ""

                            check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)

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
                                            logging.warning(f"Retry {attempt + 1} for PDF download: {pdf_link}")
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
                                     "user_id": user_id, "TOC File Name": f"{url_id}_TOC.html"})
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
            logging.error(message)
            error_list.append(message)

    try:
        try:
            response_en = http.get(url, headers=headers, timeout=30)
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
            url_cn = url.replace('/EN', '/CN')

            response_cn = http.get(url_cn, headers=headers, timeout=30)
            response_cn.raise_for_status()
            soup_cn = BeautifulSoup(response_cn.text, 'html.parser')

            chinese_heading = "<h1>Table of Contents - Chinese Version</h1>\n"
            chinese_content = soup_cn.prettify()

        except Exception as e:
            error_message = f"Error processing Chinese version of URL {url}: {str(e)}"
            error_list.append(error_message)
            print(error_message)
            chinese_heading = "<h1>Error loading Chinese version</h1>\n"
            chinese_content = f"<p>{error_message}</p>\n"

        combined_content = f"{english_heading}{english_content}<hr>{chinese_heading}{chinese_content}"

        # Save combined content to HTML file
        output_file = os.path.join(current_out, f"{url_id}_TOC.html")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(combined_content)

        print(f"Combined file saved: {output_file}")

    except Exception as e:
        print(f"Error in creating the TOC file: {e}")
        error_list.append(f"Error in creating the TOC file: {e}")

    try:
        common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                        str(len(duplicate_list)), str(len(error_list)))
    except Exception as error:
        message = f"Failed to send post request: {str(error)}"
        logging.error(message)
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
        message = f"Failed to send email: {str(error)}"
        logging.error(message)
        error_list.append(message)

    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass

except Exception as e:
    Error_message = "Error in the site: " + str(e)
    logging.error(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(
        url_id, duplicate_list, error_list, completed_list, len(completed_list),
        ini_path, attachment, current_date, current_time, Ref_value
    )
