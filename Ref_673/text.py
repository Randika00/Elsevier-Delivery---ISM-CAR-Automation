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

source_id = "316509599"

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
processed_articles = set()

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
            base_url = "http://www.ijlbpr.com/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_673.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "673"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            link = BeautifulSoup(response.content, "html.parser").find("div", class_="collapse navbar-collapse", id="navbarCollapse").find("a", class_="nav-item nav-link", string="Current Issue").get("href")

            current_link = base_url + link

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="row gx-5").findAll("div", class_="col-lg-12")
                Total_count = len(div_element)

                for single_element in div_element:
                    article_link, article_title, pdf_link = None, None, None
                    try:
                        article_title_div = single_element.find_all("strong")
                        if article_title_div:
                            for tag in article_title_div:
                                article_title = tag.text.strip()

                            doi_tag_div = single_element.find_all("br")
                            doi = ""
                            for br in doi_tag_div:
                                text = br.previous_sibling if br.previous_sibling else ""
                                if isinstance(text, str):
                                    match = re.search(r'\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b', text)
                                    if match:
                                        doi = match.group() if match else ""

                            links = single_element.find_all("a")
                            seen_links = set()
                            for link in links:
                                href = link.get("href")
                                if href:
                                    if "abstractissue" in href and href not in seen_links:
                                        article_links = href
                                        article_link = urllib.parse.urljoin(base_url, article_links)
                                        seen_links.add(href)
                                    elif "uploadfiles" in href:
                                        pdf_links = href
                                        pdf_link = urllib.parse.urljoin(base_url, pdf_links)

                            if article_link in processed_articles:
                                continue

                            elements = single_element.find_all(string=re.compile(r'Page No:'))
                            page_range = ""
                            for element in elements:
                                clean_text = re.sub(r'&nbsp;', ' ', element).strip()

                                match = re.search(r'Page No:\s*(\d+-\d+)', clean_text)
                                page_range = match.group(1) if match else None

                                volume_issue_date_info = single_element.find("h2")
                                volume, issue, month, year = "", "", "", ""
                                if volume_issue_date_info:
                                    text = volume_issue_date_info.text.strip()
                                    match = re.search(r"Volume (\d+) Issue (\d+) \((\w+)\) (\d{4})", text)
                                    if match:
                                        volume = match.group(1) if text else ""
                                        issue = match.group(2) if text else ""
                                        month = match.group(3) if text else ""
                                        year = match.group(4) if text else ""
                                    else:
                                        print("Could not extract publication details.")

                                check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                if Check_duplicate.lower() == "true" and check_value:
                                    message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                    duplicate_list.append(message)
                                    print("Duplicate Article :", article_title)

                                else:
                                    if pdf_link:
                                        pdf_content = get_response_with_retry(pdf_link, headers=headers).content
                                        output_filename = os.path.join(current_out, f"{pdf_count}.pdf")
                                        with open(output_filename, 'wb') as file:
                                            file.write(pdf_content)
                                        data.append(
                                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                             "ItemID": "",
                                             "Identifier": "",
                                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                             "Special Issue": "", "Page Range": page_range, "Month": month,
                                             "Day": "",
                                             "Year": year,
                                             "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                             "user_id": user_id})
                                        pdf_count += 1
                                        scrape_message = f"{article_link}"
                                        completed_list.append(scrape_message)
                                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                            write_file.write(article_link + '\n')
                                        print("Original Article :", article_link)

                                processed_articles.add(article_link)

                    except Exception as error:
                        message = f"Error link - {article_title}: {str(error)}"
                        print(f"{article_title}: {str(error)}")
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
                                                             len(completed_list), ini_path, attachment,
                                                             current_date,
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
