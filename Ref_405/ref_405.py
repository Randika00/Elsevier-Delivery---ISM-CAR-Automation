import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from googletrans import Translator
from datetime import datetime
import os
import common_function
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

translator = Translator()

source_id = "948141015"

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
        Error_message = "Error in the urlDetails.txt file: " + str(error)
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
            pass
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://ejvs.journals.ekb.eg"
            article_link_tag = "https://ejvs.journals.ekb.eg/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_405.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "405"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            link = BeautifulSoup(response.content, "html.parser").find("ul", class_="nav navbar-nav").find("ul", class_="dropdown-menu").find("a").get("href").replace(".", "")
            current_link = base_url + link

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="col-lg-9 col-md-9 col-sm-8 col-lg-push-3 col-md-push-3 col-sm-push-4").findAll("div")

                Total_count = len(div_element)
                all_articles_text = soup.find("div", class_="page-header margin-top-3").find("span", class_="badge badge-light")
                if all_articles_text:
                    all_articles = all_articles_text.text.strip()
                    print(f"Total number of articles: {all_articles}")

                processed_titles = set()
                processed_dois = set()
                processed_pdf_links = set()

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h5", class_="margin-bottom-6 list-article-title ltr")
                        if article_title_div:
                            article_title = article_title_div.find("a", class_="tag_a").text.strip()
                            article_links = article_title_div.find("a", class_="tag_a").get('href')
                            article_link = urllib.parse.urljoin(article_link_tag, article_links)

                            if article_title not in processed_titles:
                                processed_titles.add(article_title)

                                pages_tag = single_element.find("p", class_="margin-bottom-3").find("span")
                                page_range = ""
                                if pages_tag:
                                    page_range = pages_tag.text.strip() if pages_tag else ""

                                doi_tag = single_element.find("p", class_="margin-bottom-3 ltr", id="ar_doi")
                                doi = ""
                                if doi_tag:
                                    doi = doi_tag.find("span", dir="ltr").find("a").get('href').replace("https://doi.org/", "") if doi_tag else ""

                                    if doi not in processed_dois:
                                        processed_dois.add(doi)

                                pdf_url_text = single_element.find("ul", class_="list-inline size-12 margin-top-10 margin-bottom-3 size-14").findAll("li")[1]
                                pdf_link = ""
                                if pdf_url_text:
                                    pdf_url = pdf_url_text.find("a", class_="pdf_link").get('href').replace(".", "") if pdf_url_text else ""
                                    pdf_link = urllib.parse.urljoin(base_url, pdf_url)

                                    if pdf_link not in processed_pdf_links:
                                        processed_pdf_links.add(pdf_link)

                                volume_issue_date_info = soup.find("div", class_="weight-200 nomargin-top").findAll("span")[1]
                                volume, issue, month, year = "", "", "", ""
                                if volume_issue_date_info:
                                    volume_issue_date_text = volume_issue_date_info.text.strip()
                                    match = re.search(r"Volume (\d+), Issue (\d+), (\w+) (\d+)", volume_issue_date_text)
                                    if match:
                                        volume = match.group(1) if volume_issue_date_text else ""
                                        issue = match.group(2) if volume_issue_date_text else ""
                                        month = match.group(3) if volume_issue_date_text else ""
                                        year = match.group(4) if volume_issue_date_text else ""

                                    else:
                                        print("No match found for volume, issue, month and year.")

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
                                         "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "",
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
            Error_message = "Error in the site: " + str(e)
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