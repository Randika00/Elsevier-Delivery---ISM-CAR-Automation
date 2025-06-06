import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import os
import common_function

source_id = "79811599"

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
        read_content = []

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://jddonline.com"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_204.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "204"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = requests.get(url, headers=headers)
            current_link = BeautifulSoup(response.content, "html.parser").find("a", string="Current Issue")['href']

            response = requests.get(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="col span_9").findAll("li")

                Total_count = len(div_element)
                # print(f"Total number of articles: {Total_count}", "\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h3")
                        if article_title_div:
                            article_title = article_title_div.find("a").text.strip()
                            article_link = article_title_div.find("a").get('href')

                            volume_issue_year_info = soup.find("h3")
                            month, year, volume, issue = "", "", "", ""
                            if volume_issue_year_info:
                                match = re.search(r'(\w+)\s(\d+)\s\|\sVolume\s(\d+)\s\|\sIssue\s(\d+)',
                                                  volume_issue_year_info.text.strip())
                                if match:
                                    month = match.group(1)
                                    year = match.group(2)
                                    volume = match.group(3)
                                    issue = match.group(4)

                                article_response = requests.get(article_link, headers=headers)
                                if article_response.status_code == 200:
                                    article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                    identifier_info = article_soup.find("h3", class_="issue-info")
                                    identifier = ""
                                    if identifier_info:
                                        identifier_text = identifier_info.text.strip()
                                        parts = identifier_text.split('|')
                                        if len(parts) >= 3:
                                            identifier = parts[-2].strip()

                                    pdf_link_tag = article_soup.find("div", class_="article-purchase-widget").find("a", href=re.compile("download.php|/cart/"))
                                    pdf_url = ""
                                    if pdf_link_tag:
                                        pdf_link = pdf_link_tag['href']
                                        if not pdf_link.startswith("http"):
                                            pdf_url = base_url + pdf_link
                                        else:
                                            pdf_url = pdf_link

                                    doi_tag = article_soup.find("div", class_="abstract")
                                    doi = ""
                                    if doi_tag:
                                        doi_text_elements = doi_tag.find_all(string=re.compile(r'doi:\d+\.\d+/JDD\.\d+'))
                                        if doi_text_elements:
                                            doi_text = doi_text_elements[0]
                                            doi_match = re.search(r'(doi:\d+\.\d+/JDD\.\d+)', doi_text)
                                            if doi_match:
                                                doi = doi_match.group(1).replace("doi:", "")
                                        else:
                                            doi = ""

                                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                    if Check_duplicate.lower() == "true" and check_value:
                                        message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                        duplicate_list.append(message)
                                        print("Duplicate Article :", article_title)

                                    else:
                                        if pdf_url:
                                            pdf_content = requests.get(pdf_url, headers=headers).content
                                            output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                            with open(output_fimeName, 'wb') as file:
                                                file.write(pdf_content)
                                        data.append(
                                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                             "Identifier": identifier,
                                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                             "Special Issue": "", "Page Range": "", "Month": month, "Day": "",
                                             "Year": year,
                                             "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf" if pdf_url else "",
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
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except Exception as error:
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
