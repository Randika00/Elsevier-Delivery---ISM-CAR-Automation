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

source_id = "664439338"

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
            base_url = "http://jkspe.kspe.or.kr"
            article_link_tag = "http://jkspe.kspe.or.kr/_common/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_1206.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "1206"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            response.encoding = "utf-8"

            soup = BeautifulSoup(response.text, "html.parser")
            link = soup.find("ul", class_="depth_1").findAll("ol", class_="depth_2")[1].find("a", string="Current Issue").get("href")
            current_link = base_url + link

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="sub_contents").findAll("table", {"cellpadding": "0", "cellspacing": "0", "border": "0", "class": "", "width": "100%"})

                Total_count = len(div_element)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h5")
                        if article_title_div:
                            article_title = article_title_div.find("a").text.strip()
                            article_links = article_title_div.find("a").get('href')
                            article_link = urllib.parse.urljoin(article_link_tag, article_links)

                            doi_tags = single_element.findAll("span", class_="searchView_date")
                            doi = ""
                            if len(doi_tags) > 1:
                                doi_link = doi_tags[1].find("a")
                                doi = doi_link.get('href').replace("https://doi.org/", "") if doi_link else ""

                            volume_issue_info = soup.find("div", class_="book_select_name")
                            volume, issue = "", ""
                            if volume_issue_info:
                                if volume_issue_info:
                                    text = volume_issue_info.get_text(strip=True)

                                    volume_match = re.search(r"Vol\.\s*(\d+)", text)
                                    issue_match = re.search(r"No\.\s*(\d+)", text)

                                    if volume_match:
                                        volume = volume_match.group(1) if volume_match else ""
                                    if issue_match:
                                        issue = issue_match.group(1) if issue_match else ""

                                else:
                                    print("No match found for volume, issue.")

                            pdf_url_tag = single_element.find("div", style="line-height:130%;padding-top: 5px;").findAll("a")[1]
                            pdf_link = ""
                            if pdf_url_tag:
                                pdf_links = pdf_url_tag.get('href') if pdf_url_tag else ""
                                pdf_link = urllib.parse.urljoin(base_url, pdf_links)

                            article_response = get_response_with_retry(article_link, headers=headers)
                            if article_response.status_code == 200:
                                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                pages_tags = article_soup.find("table", {"width": "100%", "class": "fm"}).findAll("td", {"valign": "top"})
                                page_range = ""
                                for pages_tag in pages_tags:
                                    text = pages_tag.get_text(strip=True)

                                    page_range_match = re.search(r"pp\.\s*(\d+-\d+)", text)

                                    if page_range_match:
                                        page_range = page_range_match.group(1) if page_range_match else ""

                                year_info = article_soup.find("table", {"width": "100%", "class": "fm"}).findAll("tr")[5]
                                year = ""
                                if year_info:
                                    text = year_info.get_text(strip=True)

                                    year_match = re.search(r"\b(\d{4})\b", text)

                                    if year_match:
                                        year = year_match.group(1) if year_match else ""

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