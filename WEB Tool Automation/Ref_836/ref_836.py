import os
import pandas as pd
import requests
import re
import urllib3
from bs4 import BeautifulSoup
import common_function
from googletrans import Translator
from datetime import datetime
import certifi
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

url_id = "79734999"

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

# Function to create a session with retries
def create_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

try:
    url = "https://nsuworks.nova.edu/tqr/"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_836.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "836"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    session = create_session()

    response = session.get(url, headers=headers, verify=certifi.where())
    soup = BeautifulSoup(response.text, 'html.parser')

    div_element = soup.find("div", class_="article-list").findAll("div", class_="doc")
    Total_count = len(div_element)
    print(f"Total number of articles:{Total_count}", "\n")

    for single_element in div_element:
        article_link, article_title = None, None
        try:
            article_link_tag = single_element.findAll("p")[1].find("a")
            article_link = article_link_tag['href']

            article_title = article_link_tag.text.strip()

            volume_issue_month_info = soup.find("h1").text.strip()

            pattern = r"Volume (\d+).*?Number (\d+).*?-\s+(\w+)\s+(\d{4})"

            match = re.search(pattern, volume_issue_month_info)
            volume, issue, month, year = "", "", "", ""
            if match:
                volume = match.group(1) if pattern else ""
                issue = match.group(2) if pattern else ""
                month = match.group(3) if pattern else ""
                year = match.group(4) if pattern else ""
            else:
                print("No match found")

            article_response = session.get(article_link, headers=headers, verify=certifi.where())
            if article_response.status_code == 200:
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                pdf_url = article_soup.find("div", class_="aside download-button").find("a", class_="btn").get("href")

                doi_tag = article_soup.find("div", id="doi", class_="element")
                doi = ""
                if doi_tag:
                    doi = doi_tag.find("p").text.strip() if doi_tag else ""

                div_elements = article_soup.find("div", class_="element", id="recommended_citation")
                page_range = ""
                if div_elements:
                    citation_text = div_elements.find("p").text.strip()

                    page_pattern = r"(\d{4})-(\d{4})"
                    page_match = re.search(page_pattern, citation_text)

                    if page_match:
                        page_range = page_match.group(0) if citation_text else ""
                    else:
                        print("No page range found.")

                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)
                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print("Duplicate Article :", article_title)

                    else:
                        pdf_content = session.get(pdf_url, headers=headers, verify=certifi.where()).content
                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_fimeName, 'wb') as file:
                            file.write(pdf_content)
                        data.append(
                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                             "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "",
                             "Year": year,
                             "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
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
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
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
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
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
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)