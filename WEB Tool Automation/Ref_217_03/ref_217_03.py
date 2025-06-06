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

# Initialize the translator
translator = Translator()

source_id = "290220199"

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

# Retry strategy for requests
retry_strategy = Retry(
    total=3,  # Retry up to 3 times
    status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

try:
    try:
        with open('urlDetails.txt', 'r', encoding='utf-8') as file:
            url_details = file.readlines()
    except Exception as error:
        error_message = "Error in the urlDetails.txt file: " + str(error)
        print(error_message)
        error_list.append(error_message)
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
            base_url = "https://revistaseug.ugr.es"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_217_03.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "217_03"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = http.get(url, timeout=10)
            link = BeautifulSoup(response.content, "html.parser").find("ul", class_="issues_archive").find("div", class_="obj_issue_summary").find("h2").find("a", class_="title").get('href')
            link_id = link.split('/')[-1]
            current_link = f"https://revistaseug.ugr.es/index.php/RELIEVE/user/setLocale/en_US?source=%2Findex.php%2FRELIEVE%2Fissue%2Fview%2F{link_id}"

            response = http.get(current_link, timeout=10)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_elements = soup.find("div", class_="sections").findAll("div", class_="obj_article_summary")

                total_count = len(div_elements)
                print(f"Total number of articles: {total_count}")

                for single_element in div_elements:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h3", class_="title")
                        if article_title_div:
                            article_title = article_title_div.find("a").text.strip()
                            article_link = article_title_div.find("a").get('href')

                            volume_year_info = soup.find("h1").get_text(strip=True)
                            pattern = r"Vol\. (\d+) No\. (\d+) \((\d{4})\)"
                            match = re.search(pattern, volume_year_info)
                            if match:
                                volume = match.group(1)
                                issue = match.group(2)
                                year = match.group(3)
                            else:
                                raise ValueError("Volume, issue, or year not found in the string")

                            article_response = http.get(article_link, headers=headers, timeout=10)
                            if article_response.status_code == 200:
                                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                doi_tag = article_soup.find("section", class_="item doi")
                                doi = ""
                                if doi_tag:
                                    doi = doi_tag.find("span", class_="value").find("a").get('href').replace("https://doi.org/", "")

                                last_page_text = single_element.find("ul", class_="galleys_links")
                                last_page_link = ""
                                if last_page_text:
                                    last_page_link = last_page_text.findAll("li")[1].find("a", class_="obj_galley_link pdf").get('href')

                                    last_response = http.get(last_page_link, headers=headers, timeout=10)
                                    if last_response.status_code == 200:
                                        last_soup = BeautifulSoup(last_response.text, "html.parser")

                                        url_text = last_soup.find("header", class_="header_view")
                                        if url_text:
                                            pdf_url_tag = url_text.find("a", class_="download")
                                            pdf_link = ""
                                            if pdf_url_tag:
                                                pdf_link = pdf_url_tag.get("href")

                                            check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                            if Check_duplicate.lower() == "true" and check_value:
                                                message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                                duplicate_list.append(message)
                                                print(f"Duplicate Article: {article_title}")

                                            else:
                                                pdf_content = http.get(pdf_link, headers=headers, timeout=10).content
                                                output_filename = os.path.join(current_out, f"{pdf_count}.pdf")
                                                with open(output_filename, 'wb') as file:
                                                    file.write(pdf_content)
                                                data.append(
                                                    {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                     "ItemID": "", "Identifier": "", "Volume": volume, "Issue": issue,
                                                     "Supplement": "", "Part": "", "Special Issue": "", "Page Range": "",
                                                     "Month": "", "Day": "", "Year": year, "URL": article_link,
                                                     "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                                                df = pd.DataFrame(data)
                                                df.to_excel(out_excel_file, index=False)
                                                pdf_count += 1
                                                scrape_message = f"{article_link}"
                                                completed_list.append(scrape_message)
                                                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                                    write_file.write(article_link + '\n')
                                                print(f"Original Article: {article_link}")

                    except Exception as error:
                        message = f"Error link - {article_title}: {str(error)}"
                        print(message)
                        error_list.append(message)

                try:
                    common_function.sendCountAsPost(source_id, Ref_value, str(total_count), str(len(completed_list)),
                                                    str(len(duplicate_list)), str(len(error_list)))
                except Exception as error:
                    message = f"Failed to send post request: {str(error)}"
                    print(message)
                    error_list.append(message)

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
                    print(message)
                    error_list.append(message)

                sts_file_path = os.path.join(current_out, 'Completed.sts')
                with open(sts_file_path, 'w') as sts_file:
                    pass

        except Exception as e:
            error_message = f"Error in the site: {str(e)}"
            print(error_message)
            error_list.append(error_message)
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except Exception as error:
    error_message = f"General error: {str(error)}"
    print(error_message)
    error_list.append(error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
