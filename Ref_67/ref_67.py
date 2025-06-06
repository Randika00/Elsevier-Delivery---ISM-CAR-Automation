import time
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
import common_function
from tenacity import retry, stop_after_attempt, wait_fixed
import logging

logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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

month_mapping = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June",
    "Jul": "July",
    "Aug": "August",
    "Sep": "September",
    "Oct": "October",
    "Nov": "November",
    "Dec": "December"
}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def fetch_url(url, headers):
    return requests.get(url, headers=headers)

try:
    try:
        with open('urlDetails.txt', 'r', encoding='utf-8') as file:
            url_details = file.readlines()
    except Exception as error:
        Error_message = "Error in the urlDetails.txt file: " + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                             ini_path, attachment, current_date, current_time, Ref_value)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'journals.ametsoc.org',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
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
            time.sleep(30)
            if ',' in line:
                url, source_id = line.strip().split(",", 1)
                source_id = source_id.strip()
                base_url = "https://journals.ametsoc.org"
            else:
                continue

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_67.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "67"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1
            attachment = None

            response = fetch_url(url, headers=headers)
            time.sleep(10)
            link = BeautifulSoup(response.content, "html.parser").findAll("div", class_="pattern-library-style-root")[7].find("a", class_="c-Button c-Button--secondary c-Button--large c-Button--contained").get('href')

            current_link = base_url + link

            response = fetch_url(current_link, headers=headers)
            time.sleep(10)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.findAll("div", class_="type-article leaf")

                Total_count = len(div_element)
                # print(f"Total number of articles: {Total_count}", "\n")

                for title_element in soup.find_all('h1', class_='typography-body text-display4 font-ui fw-3 color-primary f-4 ln-3'):

                    article_link, article_title = None, None
                    try:
                        article_title = title_element.text.strip()
                        url_element = title_element.find('a')
                        if url_element:
                            article_link = "https://journals.ametsoc.org" + url_element.get('href')

                            pdf_urls = article_link.replace("/view/", "/downloadpdf/")
                            pdf_link = pdf_urls.replace(".xml", ".pdf")

                            pdf_url = pdf_link.replace("/downloadpdf/", "/downloadpdf/view/")

                            doi_elements = title_element.find_all('a', class_='c-Button--link', href=True)
                            doi = [f"10.1175/{doi_element['href'].split('/')[-1].replace('.xml', '')}" for doi_element in doi_elements]
                            doi = ', '.join(doi)

                            issue_info = soup.find('h1', class_='typography-body title mb-3 text-headline font-content')

                            volume, issue, year, month_full = "", "", "", ""
                            if issue_info:
                                issue_text = issue_info.text.strip()
                                match = re.search(r'Volume (\d+) \((\d{4})\): Issue (\d+) \((\w{3}) (\d{4})\)', issue_text)

                                if match:
                                    volume = match.group(1)
                                    year = match.group(2)
                                    issue = match.group(3)
                                    month_abbreviated = match.group(4)
                                    month_full = month_mapping.get(month_abbreviated, month_abbreviated)

                            page_range_element = title_element.find_next("dd", class_="pagerange inline c-List__item c-List__item--secondary text-metadata-value")

                            page_range = ""
                            if page_range_element:
                                page_range = page_range_element.text.strip() if page_range_element else ""

                            check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                            if Check_duplicate.lower() == "true" and check_value:
                                message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                duplicate_list.append(message)
                                print("Duplicate Article :", article_title)

                            else:
                                time.sleep(10)
                                pdf_content = fetch_url(pdf_url, headers=headers).content
                                output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                with open(output_fimeName, 'wb') as file:
                                    file.write(pdf_content)
                                data.append(
                                    {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                     "Identifier": "",
                                     "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                     "Special Issue": "", "Page Range": page_range, "Month": month_full, "Day": "",
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
                        message = f"Error link - {article_title} : {str(error)}"
                        print(f"{article_title} : {str(error)}")
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
