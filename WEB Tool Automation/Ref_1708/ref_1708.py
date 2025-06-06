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

source_id = "79733799"

duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
time_prefix = None
today_date = None
volume = None
ini_path = None

def create_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

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
            base_url = "https://reis.cis.es"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_1708.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "1708"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            session = create_session()

            response = session.get(url, timeout=10)

            link = BeautifulSoup(response.content, "html.parser").find("ul", class_="issues_archive").find("div", class_="obj_issue_summary").find("h2").find("a", class_="title").get('href')
            link_id = link.split('/')[-1]
            current_link = f"https://reis.cis.es/index.php/reis/user/setLocale/en_US?source=%2Findex.php%2Freis%2Fissue%2Fview%2F{link_id}"

            response = session.get(current_link, timeout=10)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_elements = soup.find("div", class_="sections").findAll("div", class_="obj_article_summary")
                Total_count = len(div_elements)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_elements:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h3", class_="title")
                        article_url = article_title_div.find("a")

                        article_title = article_url.get_text(separator=" ", strip=True)

                        article_link_div = single_element.find("h3", class_="title")
                        if article_link_div:
                            article_link = article_link_div.find("a").get('href')

                            issue_year_info = soup.find("h1").get_text(strip=True)
                            issue_match = re.search(r'No\.\s*(\d+)', issue_year_info)
                            year_match = re.search(r'\((\d{4})\)', issue_year_info)

                            issue = issue_match.group(1) if issue_match else ""
                            year = year_match.group(1) if year_match else ""

                            month_info = soup.find("div", class_="published").find("span", class_="value")
                            month = ""
                            if month_info:
                                published_date_text = month_info.text.strip()
                                month_match = re.search(r'(\d{4}-\d{2}-\d{2})', published_date_text)
                                if month_match:
                                    date_str = month_match.group(1) if month_match else ""
                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                    month_number = date_obj.month
                                    month_name = date_obj.strftime('%B')
                                    month = month_name

                            last_page_text = single_element.find("ul", class_="galleys_links")
                            last_page_link = ""
                            if last_page_text:
                                last_page_link = last_page_text.find("a", class_="obj_galley_link pdf").get('href')

                                last_response = session.get(last_page_link, timeout=10)
                                if last_response.status_code == 200:
                                    last_soup = BeautifulSoup(last_response.text, "html.parser")

                                    url_text = last_soup.find("header", class_="header_view")
                                    pdf_link = ""
                                    if url_text:
                                        pdf_url_tag = url_text.find("a", class_="download")
                                        if pdf_url_tag:
                                            pdf_link = pdf_url_tag.get("href") if pdf_url_tag else ""

                                    article_response = session.get(article_link, headers=headers, timeout=10)
                                    if article_response.status_code == 200:
                                        article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                        doi_tag = article_soup.find("section", class_="item doi")
                                        doi = ""
                                        if doi_tag:
                                            doi = doi_tag.find("span", class_="value").find("a").get('href').replace("https://doi.org/", "") if doi_tag else ""

                                        pages_range_text = article_soup.find("div", class_="")
                                        page_range = ""
                                        if pages_range_text:
                                            pages_tag = pages_range_text.find("div", class_="csl-entry")
                                            if pages_tag:
                                                page_range_match = re.search(r'\b(\d+\s*–\s*\d+)\b', pages_tag.get_text())
                                                if page_range_match:
                                                    page_range = page_range_match.group(1) if pages_tag else ""
                                                else:
                                                    print("Page range not found.")

                                            check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                            if Check_duplicate.lower() == "true" and check_value:
                                                message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                                duplicate_list.append(message)
                                                print("Duplicate Article :", article_title)

                                            else:
                                                pdf_content = session.get(pdf_link, headers=headers, timeout=10).content
                                                output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                                with open(output_fimeName, 'wb') as file:
                                                    file.write(pdf_content)
                                                data.append(
                                                    {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                     "ItemID": "",
                                                     "Identifier": "",
                                                     "Volume": "", "Issue": issue, "Supplement": "", "Part": "",
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




