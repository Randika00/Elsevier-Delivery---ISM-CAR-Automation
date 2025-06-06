import os
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"],
    backoff_factor=1
)

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
source_id = None
time_prefix = None
today_date = None
ini_path = None

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

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_72.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "72"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = session.get(url, headers=headers)
            current_link = BeautifulSoup(response.content, "html.parser").find("div", id="issues").find("h4").find("a").get("href")

            response = session.get(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                all_tables = soup.find("div", id="content").findAll("table", class_="tocArticle")

                Total_count = len(all_tables)
                print(f"Total number of articles:{Total_count}", "\n")

                for single_table in all_tables:
                    article_link, article_title = None, None
                    try:
                        article_title = single_table.find("div", class_= "tocTitle").text.strip()

                        article_link = single_table.find("div", class_="tocTitle").find('a').get('href')

                        page_range = single_table.find("div", class_="tocPages").text.strip()

                        breadcrumb_div = soup.find("div", id="breadcrumb")
                        if breadcrumb_div:
                            volume_issue_text = breadcrumb_div.find_all("a")[-1].text.strip()
                            volume_issue_parts = volume_issue_text.split(",")
                            if len(volume_issue_parts) == 2:
                                volume, issue = volume_issue_parts[0].split()[-1], volume_issue_parts[1].split()[-1]
                            else:
                                volume = "Volume not found"
                                issue = "Issue not found"
                        else:
                            volume = "Volume not found"
                            issue = "Issue not found"

                        month_year_tag = soup.find("h3")
                        if month_year_tag:
                            month_year_text = month_year_tag.text.strip()
                            month, year = month_year_text.split()[0], month_year_text.split()[1]
                        else:
                            month = "Month not found"
                            year = "Year not found"

                        url_response = session.get(article_link)
                        url_soup = BeautifulSoup(url_response.text, "html.parser")
                        doi_tag = url_soup.find("a", id="pub-id::doi")
                        doi = "10.11591/" + doi_tag["href"].split("/")[-1]

                        pdf_link = url_soup.find('a', class_="file").get('href')
                        if pdf_link.startswith("http"):
                            actual_pdf_url = pdf_link.replace("/view/", "/viewFile/")
                        else:
                            actual_pdf_url = f"https://ijece.iaescore.com{pdf_link.replace('/view/', '/viewFile/')}"

                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)
                        if Check_duplicate.lower() == "true" and check_value:
                            message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                            duplicate_list.append(message)
                            print("Duplicate Article :", article_title)

                        else:
                            pdf_content = session.get(actual_pdf_url, headers=headers).content
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
