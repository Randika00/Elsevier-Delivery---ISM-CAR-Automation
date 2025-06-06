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

source_id = "924648807"

duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
time_prefix = None
today_date = None
issue = None
ini_path = None

# Set up retry strategy
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
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

            ini_path = os.path.join(os.getcwd(), "Ref_217_02.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "217_02"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = http.get(url,  timeout=10)
            link = BeautifulSoup(response.content, "html.parser").find("div", class_="issue-summary media").find("h2", class_="media-heading").find("a", class_="title").get('href')
            link_id = link.split('/')[-1]
            current_link = f"https://revistaseug.ugr.es/index.php/cpag/user/setLocale/en_US?source=%2Findex.php%2Fcpag%2Fissue%2Fview%2F{link_id}"

            response = http.get(current_link, timeout=10)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_elements = soup.find("div", class_="sections").findAll("div", class_="article-summary media")

                Total_count = len(div_elements)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_elements:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h3", class_="media-heading")
                        if article_title_div:
                            article_title = article_title_div.find("a").text.strip()
                            translated_title = translator.translate(article_title, src='es', dest='en').text
                            formatted_title = article_title.upper()
                            article_link = article_title_div.find("a").get('href')

                            doi_tag = single_element.find("div", class_="meta-doi")
                            doi = ""
                            if doi_tag:
                                doi = doi_tag.find("a").get('href').replace("https://doi.org/", "") if doi_tag else ""

                            pages_info = single_element.find("div", class_="meta-pages")
                            page_range = ""
                            if pages_info:
                                page_range = pages_info.get_text(strip=True).replace("Pages", "").strip() if pages_info else ""

                            volume_year_info = soup.find("div", class_="issue-details col-md-9")
                            volume, year = "", ""
                            if volume_year_info:
                                volume_text = volume_year_info.find("h2").get_text(strip=True)
                                volume = re.search(r'Vol\.\s(\d+)', volume_text).group(1) if re.search(r'Vol\.\s(\d+)', volume_text) else ""

                                year = re.search(r'\((\d{4})\)', volume_text).group(1) if re.search(r'\((\d{4})\)', volume_text) else ""

                            article_response = http.get(article_link, headers=headers, timeout=10)
                            if article_response.status_code == 200:
                                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                last_page_link = article_soup.find("div", class_="download").find("a", class_="galley-link btn btn-primary pdf").get('href')

                                last_response = http.get(last_page_link, headers=headers, timeout=10)
                                if last_response.status_code == 200:
                                    last_soup = BeautifulSoup(last_response.text, "html.parser")
                                    pdf_url_tag = last_soup.find("a", class_="download")
                                    pdf_url = ""
                                    if pdf_url_tag:
                                        pdf_url = pdf_url_tag.get("href")

                                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                    if Check_duplicate.lower() == "true" and check_value:
                                        message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                        duplicate_list.append(message)
                                        print("Duplicate Article :", article_title)

                                    else:
                                        pdf_content = http.get(pdf_url, headers=headers, timeout=10).content
                                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                        with open(output_fimeName, 'wb') as file:
                                            file.write(pdf_content)
                                        data.append(
                                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                             "Identifier": "",
                                             "Volume": volume, "Issue": "", "Supplement": "", "Part": "",
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
                        message = f"Error link - {article_title} : {str(error)}"
                        print(f"{article_title} : {str(error)}")
                        error_list.append(message)

                try:
                    common_function.sendCountAsPost(source_id, Ref_value, str(Total_count), str(len(completed_list)),
                                                    str(len(duplicate_list)),
                                                    str(len(error_list)))
                except Exception as error:
                    message = f"Failed to send post request : {str(error)}"
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
                    message = f"Failed to send email : {str(error)}"
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
