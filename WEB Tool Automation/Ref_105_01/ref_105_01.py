import os
import pandas as pd
import requests
import re
import urllib3
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
import certifi
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

url_id = "78849499"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

def create_session_with_retries(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = create_session_with_retries()

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
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

try:
    url = "https://ojs.sin-chn.com/index.php/mcb/issue/archive"
    base_url = "https://ojs.sin-chn.com/"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_105_01.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "105_01"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = session.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    current_link = soup.find("ul", class_="pkp_navigation_primary pkp_nav_list").findAll("li")[25].find("a")
    if current_link:
        current_link = current_link.get("href")
    else:
        raise ValueError("Main archive link not found")

    response = session.get(current_link, headers=headers, timeout=10)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        all_articles = soup.find("ul", class_="cmp_article_list articles").findAll("div", class_="bq2")

        Total_count = len(all_articles)
        # print(f"Total number of articles: {Total_count}\n")

        ul_element = soup.find("ul", class_="cmp_article_list articles").findAll("li")

        for single_element in ul_element:
            article_link, article_title = None, None
            try:
                article_link_tag = single_element.find("div", class_="bq2")
                if article_link_tag:
                    article_title = article_link_tag.find("a", class_="h3").text.strip()
                    article_link = article_link_tag.find("a", class_="h3").get("href")

                    if article_link and not article_link.startswith("http"):
                        article_link = base_url + article_link

                    volume_year_info = soup.find("div", class_="page page_issue").find("h1").text.strip()
                    volume, issue, year = "", "", ""
                    pattern = r"Vol\.\s(\d+)\sNo\.\s(\d+)\s\((\d{4})\)"

                    match = re.search(pattern, volume_year_info)
                    if match:
                        volume = match.group(1) if match else ""
                        issue = match.group(2) if match else ""
                        year = match.group(3) if match else ""

                    pdf_url_tags = single_element.findAll("ul", class_="galleys_links")
                    for pdf_tag in pdf_url_tags:
                        pdf_link = pdf_tag.find("a", class_="obj_galley_link pdf")
                        pdf_url = ""
                        if pdf_link:
                            last_page_link = pdf_link.get("href")
                            if last_page_link and not last_page_link.startswith("http"):
                                last_page_link = base_url + last_page_link

                            last_response = session.get(last_page_link, headers=headers, timeout=10)
                            last_soup = BeautifulSoup(last_response.text, "html.parser")

                            pdf_url = last_soup.find("header", class_="header_view").find("a", class_="download")
                            if pdf_url:
                                pdf_url = pdf_url.get('href')
                                if pdf_url and not pdf_url.startswith("http"):
                                    pdf_url = base_url + pdf_url

                            if pdf_url:
                                article_response = session.get(article_link, headers=headers, timeout=10)
                                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                                doi_tag = article_soup.find("div", class_="item doi").find("span", class_="value")
                                doi = doi_tag.find("a").get("href").replace("https://doi.org/", "") if doi_tag else ""

                                check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)

                                if Check_duplicate.lower() == "true" and check_value:
                                    message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                    duplicate_list.append(message)
                                    print("Duplicate Article :", article_title)
                                else:
                                    pdf_content = requests.get(pdf_url, headers=headers).content
                                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                    with open(output_fimeName, 'wb') as file:
                                        file.write(pdf_content)
                                    data.append(
                                        {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                         "Identifier": "",
                                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                         "Special Issue": "", "Page Range": "", "Month": "", "Day": "",
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

            except requests.exceptions.RequestException as req_err:
                message = f"Error link - {article_title} : {str(req_err)}"
                error_list.append(message)
            except Exception as error:
                message = f"Error link - {article_title} : {str(error)}"
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
            message = f"Failed to send email: {str(error)}"
            error_list.append(message)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass

except Exception as e:
    error_list.append(f"Error in the site: {str(e)}")
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
