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

source_id = "942267985"

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
volume = None

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

def is_valid_url(url):
    return url and (url.startswith("http://") or url.startswith("https://"))

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
            base_url = "https://phil.duan.edu.ua"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_1687.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "1687"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            if is_valid_url(url):
                response = get_response_with_retry(url, headers=headers)
                link = BeautifulSoup(response.content, "html.parser").find("td", style="padding: 12px; width: 390px; height: 15px; text-align: left;").find("span", style="color: #222222;").find("a", style="color: #222222;").get("href")
                current_link = base_url + link

                if is_valid_url(current_link):
                    response = get_response_with_retry(current_link, headers=headers)

                    if response.status_code == 200:
                        html_content = response.text
                        soup = BeautifulSoup(html_content, "html.parser")

                        div_element = soup.find("div", class_="articleBody itemBody").findAll("p")

                        Total_count = len(div_element)

                        for single_element in div_element:
                            article_link, article_title = None, None
                            try:
                                article_title_div = single_element.find("a", style="color: #5c0410;")
                                if article_title_div:
                                    article_title = article_title_div.text.strip()
                                    article_links = article_title_div.get('href')
                                    article_link = urllib.parse.urljoin(base_url, article_links)

                                    doi_tag = single_element.find("span", class_="nowrap", style="white-space: nowrap;")
                                    doi = ""
                                    if doi_tag:
                                        doi = doi_tag.text.strip()

                                    pdf_url_text = single_element.find("span", class_="nowrap", style="white-space: nowrap;")
                                    pdf_link = ""
                                    if pdf_url_text:
                                        pdf_links = pdf_url_text.find("a", style="color: #5c0410;").get('href')
                                        pdf_link = urllib.parse.urljoin(base_url, pdf_links)

                                    year_issue_info = soup.find("h3", class_="modtitle")
                                    year, issue = "", ""
                                    if year_issue_info:
                                        year_issue_text = year_issue_info.text.strip()
                                        match = re.search(r'(\d{4}) No\. (\d+ \(\d+\))', year_issue_text)

                                        if match:
                                            year = match.group(1)
                                            issue = match.group(2)

                                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                        if Check_duplicate.lower() == "true" and check_value:
                                            message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                            duplicate_list.append(message)
                                            print("Duplicate Article:", article_title)

                                        else:
                                            if is_valid_url(pdf_link):
                                                pdf_content = get_response_with_retry(pdf_link, headers=headers).content
                                                output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                                with open(output_fimeName, 'wb') as file:
                                                    file.write(pdf_content)
                                                data.append(
                                                    {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                     "ItemID": "",
                                                     "Identifier": "",
                                                     "Volume": "", "Issue": issue, "Supplement": "", "Part": "",
                                                     "Special Issue": "", "Page Range": "", "Month": "",
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
                                                print("Original Article:", article_link)

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
