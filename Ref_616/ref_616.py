import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
import calendar
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import common_function

source_id = "318298299"

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
            base_url = "https://dergipark.org.tr"
            toc_link = "https://dergipark.org.tr/en/pub/ktd"
            pdf_tag = "https://dergipark.org.tr"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_616.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "616"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            link_div = soup.find("div", class_="kt-widget-17__product-desc")
            link_id = ""
            volume, issue = "", ""
            if link_div:
                link_tag = link_div.find("a")
                link_text = link_tag["href"] if link_tag else "Link not found"
                link_id = link_text.split('/')[-1]

                volume_issue_text = link_tag.get_text(strip=True) if link_tag else ""
                match = re.search(r"Volume:\s*(\d+)\s*Issue:\s*(\d+)", volume_issue_text)
                volume = match.group(1) if match else "Not found"
                issue = match.group(2) if match else "Not found"
            else:
                print("Required div not found")

            current_link = f"https://dergipark.org.tr/en/pub/ktd/issue/{link_id}"

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="mode-list", id="articles-listing").findAll("div", class_=("card", "j-card", "article-project-actions", "article-card", "article-card-block"))
                Total_count = len(div_element)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("div", class_="card-body")
                        if article_title_div:
                            article_toc = article_title_div.find("a", class_="card-title article-title").text.strip()

                            match = re.match(r"(\d+\.)\s+(.*)", article_toc)
                            if match:
                                article_id = match.group(1)
                                article_text = match.group(2)
                                article_title = article_text
                                article_link = article_title_div.find("a", class_="card-title article-title").get('href')

                                pages_tag = single_element.find("div", class_="card-footer").find("h6", class_="card-subtitle text-muted article-page-interval")
                                page_range = ""
                                if pages_tag:
                                    pages_text = pages_tag.get_text(strip=True)

                                    match = re.search(r"Page\s*:\s*(.*)", pages_text)
                                    if match:
                                        page_range = match.group(1)
                                    else:
                                        print("page range not found")

                                year_info = soup.find("span", class_="kt-widget-12__desc").find("a", class_="btn btn-default btn-sm btn-bold btn-upper kt-aside--right")
                                year = ""
                                if year_info:
                                    year_text = year_info.get_text(strip=True)

                                    match = re.search(r"Year:\s*(\d{4})", year_text)
                                    if match:
                                        year = match.group(1)
                                    else:
                                        print("year not found")

                                pdf_link_text = single_element.find("div", class_="card-footer")
                                pdf_link = ""
                                if pdf_link_text:
                                    pdf_links = pdf_link_text.find("a", class_="article-download article-page-interval").get('href')
                                    pdf_link = urllib.parse.urljoin(pdf_tag, pdf_links)
                                else:
                                    print("pdf_link not found")

                                article_response = get_response_with_retry(article_link, headers=headers)
                                if article_response.status_code == 200:
                                    article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                    doi_tag = article_soup.find("div", class_="article-doi data-section")
                                    doi = ""
                                    if doi_tag:
                                        doi = doi_tag.find("a", class_="doi-link").text.strip().replace("https://doi.org/", "")
                                    else:
                                        print("doi not found")

                                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                    if Check_duplicate.lower() == "true" and check_value:
                                        message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                        duplicate_list.append(message)
                                        print("Duplicate Article:", article_title)

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
                                             "Special Issue": "", "Page Range": page_range, "Month": "",
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