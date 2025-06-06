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

source_id = "652414043"

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

def get_token(url):
    response = requests.get(url, headers=headers)
    # print("Cookies:", response.cookies)
    cookie = response.cookies
    token = cookie.get("wkxt3_csrf_token")

    if token:
        token = token.replace("-", "")
    else:
        print("Token not found in cookies")
        raise Exception("Token not found in cookies")

    return token

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
            base_url = "http://qdhys.ijournal.cn/hyyhze/ch/reader/"
            toc_url = "http://qdhys.ijournal.cn/hyyhze/ch/index.aspx"
            article_div = "https://www.epae.cn/dlzdhsb/ch/reader/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_524.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "524"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            table_row = soup.find("tr", height="25")

            volume_year_text = table_row.find("td").get_text(strip=True)
            volume_match = re.search(r"Vol\.(\d+),\s*(\d+)", volume_year_text)
            year = ""
            if volume_match:
                volume = volume_match.group(1) if volume_match else ""
                year = volume_match.group(2) if volume_match else ""

            latest_issue_tag = table_row.find("a", href=True)
            current_link, volume, issue = "", "", ""
            if latest_issue_tag:
                link = latest_issue_tag['href']
                current_link = base_url + link
                issue_match = re.search(r"quarter_id=(\d+)", link)
                if issue_match:
                    issue = issue_match.group(1) if issue_match else ""

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("tbody").findAll("table", {"id": "table24", "cellspacing": "0", "cellpadding": "0", "width": "100%", "border": "0"})

                Total_count = len(div_element)
                # print(f"Total number of articles: {Total_count}\n")

                printed_titles = set()
                unique_page_ranges = set()
                printed_urls = set()

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find_all("tr")
                        if article_title_div:
                            for article in article_title_div:
                                title_tag = article.find("b")
                                if title_tag:
                                    article_title = title_tag.get_text(strip=True)
                                    if article_title.lower() != "abstract" and article_title:
                                        if article_title not in printed_titles:
                                            printed_titles.add(article_title)

                                            link_tag = article.find('a', href=True)
                                            article_link = ""
                                            if link_tag:
                                                article_links = link_tag['href']
                                                article_link = urllib.parse.urljoin(base_url, article_links)

                                            page_ranges = single_element.find_all("td")
                                            page_range = ""
                                            for page in page_ranges:
                                                page_text = page.get_text(strip=True)
                                                match = re.search(r'\d{1,3}(?:-\d{1,3})?$', page_text)
                                                if match:
                                                    page_range = match.group() if page_text else ""
                                                    if page_range not in unique_page_ranges:
                                                        unique_page_ranges.add(page_range)

                                            pdf_text = single_element.find_all('a', href=True)
                                            pdf_link = ""
                                            for link in pdf_text:
                                                href = link['href']
                                                if 'create_pdf.aspx' in href:
                                                    pdf_links = href
                                                    pdf_link = urllib.parse.urljoin(article_div, pdf_links)
                                                    if pdf_link not in printed_urls:
                                                        printed_urls.add(pdf_link)

                                            article_response = get_response_with_retry(article_link, headers=headers)
                                            if article_response.status_code == 200:
                                                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                                doi_tag = article_soup.find("span", id="DOI")
                                                doi = ""
                                                if doi_tag:
                                                    a_tag = doi_tag.find("a")
                                                    if a_tag:
                                                        doi = a_tag.text.strip() if a_tag else ""
                                                    else:
                                                        print("DOI not found")
                                                else:
                                                    print("DOI not found")

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
                                                    print("Original Article :", article_link)

                    except Exception as error:
                        message = f"Error link - {article_title}: {str(error)}"
                        print(f"{article_title}: {str(error)}")
                        error_list.append(message)

                try:
                    try:
                        response_en = get_response_with_retry(toc_url, headers=headers)
                        response_en.raise_for_status()
                        soup_en = BeautifulSoup(response_en.text, 'html.parser')

                        english_heading = "<h1>Table of Contents - Chinese Version</h1>\n"
                        english_content = soup_en.prettify()

                    except Exception as e:
                        error_message = f"Error processing Chinese Version of URL {toc_url}: {str(e)}"
                        error_list.append(error_message)
                        print(error_message)
                        english_heading = "<h1>Error loading Chinese Version</h1>\n"
                        english_content = f"<p>{error_message}</p>\n"

                    combined_content = f"{english_heading}{english_content}"

                    output_file = os.path.join(current_out, f"{source_id}_TOC.html")
                    with open(output_file, 'w', encoding='utf-8') as file:
                        file.write(combined_content)

                    print(f"Combined file saved: {output_file}")

                except Exception as e:
                    print(f"Error in creating the TOC file: {e}")
                    error_list.append(f"Error in creating the TOC file: {e}")

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