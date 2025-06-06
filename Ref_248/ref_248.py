import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
import common_function
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

source_id = "943987999"

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

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(requests.exceptions.RequestException))
def make_request(url, headers):
    return requests.get(url, headers=headers)

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
            base_url = "http://zgnjhxb.niam.com.cn/EN"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_248.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "248"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = make_request(url, headers)
            current_link = BeautifulSoup(response.content, "html.parser").find("ul", class_="nav navbar-nav").findAll("li", {"role": "presentation"})[13].find("a", {"role": "menuitem"}).get("href")

            response = make_request(current_link, headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="content_nr").findAll("ul", class_="lunwen")

                Total_count = len(div_element)
                # print(f"Total number of articles:{Total_count}", "\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_link_tag = single_element.find("li", class_="biaoti")
                        if article_link_tag:
                            article_title = article_link_tag.find("a").text.strip()
                            article_link = article_link_tag.find("a").get("href")

                            volume_issue_info = single_element.findAll("li")[2]
                            if volume_issue_info:
                                volume_issue_text = volume_issue_info.find("span", class_="nianqi").text.strip()
                                match = re.search(r"(\d{4}), (\d+) \((\d+)\): (\d+-\d+)", volume_issue_text)
                                year, volume, issue, page_range = "", "", "", ""
                                if match:
                                    year = match.group(1)
                                    volume = match.group(2)
                                    issue = match.group(3)
                                    page_range = match.group(4)

                                doi_tag = single_element.findAll("li")[2]
                                doi = ""
                                if doi_tag:
                                    doi = doi_tag.findAll("span", class_="doi")[1].text.strip().replace("DOI:","")

                                onclick_attr = single_element.find("li", class_="zhuyao-anniu")
                                if onclick_attr:
                                    onclick_text = onclick_attr.findAll("a")[1].get("onclick")
                                    id_match = re.search(r"lsdy1\('PDF','(\d+)',", onclick_text)
                                    pdf_id, pdf_link = "", ""
                                    if id_match:
                                        pdf_id = id_match.group(1)

                                        base_pdf_url = "http://zgnjhxb.niam.com.cn/EN/article/downloadArticleFile.do?attachType=PDF&id="

                                        pdf_link = base_pdf_url + str(pdf_id)

                                    day_month_info = soup.find("div", class_="journal-info").find("p")
                                    if day_month_info:
                                        date_text = day_month_info.text.strip()
                                        date_match = re.search(r"Publication date:(\d{1,2}) (\w+)", date_text)
                                        day, month = "", ""
                                        if date_match:
                                            day = date_match.group(1)
                                            month = date_match.group(2)

                                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                        if Check_duplicate.lower() == "true" and check_value:
                                            message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                            duplicate_list.append(message)
                                            print("Duplicate Article :", article_title)

                                        else:
                                            pdf_content = make_request(pdf_link, headers).content
                                            output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                            with open(output_fimeName, 'wb') as file:
                                                file.write(pdf_content)
                                            data.append(
                                                {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                 "ItemID": "",
                                                 "Identifier": "",
                                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                 "Special Issue": "", "Page Range": page_range, "Month": month, "Day": day,
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
