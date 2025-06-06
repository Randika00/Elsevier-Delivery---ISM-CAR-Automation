import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
import common_function
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Initialize lists and variables
duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
time_prefix = None
source_id = None
today_date = None
ini_path = None

# Define retry strategy
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Function to read file content safely
def read_file_safely(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except Exception as e:
        error_msg = f"Error in the {file_path} file: {str(e)}"
        print(error_msg)
        error_list.append(error_msg)
        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                             ini_path, attachment, current_date, current_time, Ref_value)
        return None

# Read URL details
url_details = read_file_safely('urlDetails.txt')
if not url_details:
    exit()

try:
    try:
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
    except FileNotFoundError:
        with open('completed.txt', 'w', encoding='utf-8'):
            with open('completed.txt', 'r', encoding='utf-8') as read_file:
                read_content = read_file.read().split('\n')

    # Define headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    # Process each URL
    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://scipost.org"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_226.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "226"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            # Get the initial page
            response = http.get(url, headers=headers, timeout=10)
            link = BeautifulSoup(response.content, "html.parser").findAll("div", class_="col-12")[2].find("li").find("a").get("href")
            current_link = base_url + link

            response = http.get(current_link, headers=headers, timeout=10)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("ul", class_="list-unstyled").findAll("li")

                Total_count = len(div_element)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("div", class_="card-header")
                        if article_title_div:
                            article_title = article_title_div.find("h3", class_="my-0").find("a").text.strip()

                            article_link_tag = single_element.find("div", class_="card-header")
                            article_links = article_link_tag.find("h3", class_="my-0").find("a").get('href')
                            article_link = urllib.parse.urljoin(base_url, article_links)

                            identifier_tag = single_element.find("p", class_="card-text text-muted")
                            identifier = ""
                            if identifier_tag:
                                identifier_text = identifier_tag.text
                                match = re.search(r'SciPost Phys\..*?, (\d+)', identifier_text)
                                if match:
                                    identifier = match.group(1) if match else ""

                                volume_issue_info = soup.find("span", class_="breadcrumb-item active")
                                volume, issue = "", ""
                                if volume_issue_info:
                                    volume_issue_text = volume_issue_info.text
                                    volume_issue_match = re.search(r'Vol\. (\d+) issue (\d+)', volume_issue_text)
                                    if volume_issue_match:
                                        volume = volume_issue_match.group(1) if volume_issue_match else ""
                                        issue = volume_issue_match.group(2) if volume_issue_match else ""

                                    month_year_info = soup.find("h2", class_="text-blue m-0 p-0 py-2")
                                    month, year = "", ""
                                    if month_year_info:
                                        month_year_text = month_year_info.text

                                        month_match = re.search(
                                            r'(January|February|March|April|May|June|July|August|September|October|November|December)',
                                            month_year_text)
                                        year_match = re.search(r'(\d{4})', month_year_text)
                                        month = month_match.group(1) if month_match else ""
                                        year = year_match.group(1) if year_match else ""

                                    article_response = http.get(article_link, headers=headers, timeout=10)
                                    if article_response.status_code == 200:
                                        article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                        doi_tag = article_soup.find("ul", class_="publicationClickables mt-3")
                                        doi = ""
                                        if doi_tag:
                                            doi_li = doi_tag.find("li")
                                            if doi_li and "doi:" in doi_li.text:
                                                doi_text = doi_li.text.strip()
                                                doi_info = re.search(r'doi:\s*(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', doi_text, re.I)
                                                if doi_info:
                                                    doi = doi_info.group(1) if doi_info else ""

                                            pdf_link_info = article_soup.find("li", class_="publicationPDF")
                                            pdf_url = ""
                                            if pdf_link_info:
                                                pdf_href = pdf_link_info.find("a").get("href")
                                                pdf_url = urllib.parse.urljoin(base_url, pdf_href)

                                                check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                                if Check_duplicate.lower() == "true" and check_value:
                                                    message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                                    duplicate_list.append(message)
                                                    print("Duplicate Article:", article_title)

                                                else:
                                                    pdf_content = http.get(pdf_url, headers=headers, timeout=10).content
                                                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                                    with open(output_fimeName, 'wb') as file:
                                                        file.write(pdf_content)
                                                    data.append(
                                                        {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                         "ItemID": "",
                                                         "Identifier": identifier,
                                                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                         "Special Issue": "", "Page Range": "", "Month": month,
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

                try:
                    common_function.sendCountAsPost(source_id, Ref_value, str(Total_count),
                                                    str(len(completed_list)),
                                                    str(len(duplicate_list)), str(len(error_list)))
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
    Error_message = "General error :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)


