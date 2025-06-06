import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
import urllib3
from urllib.parse import urljoin
from datetime import datetime
import os
import common_function
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

source_id = "76721499"

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

def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
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
        exit()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    try:
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
    except FileNotFoundError:
        open('completed.txt', 'w', encoding='utf-8').close()
        read_content = []

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://erj.ersjournals.com/"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_233.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "233"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = requests_retry_session().get(url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch URL: {url}")

            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")
            menu_ul = soup.select_one("ul.menu")
            current_link = None

            if menu_ul:
                current_issue_a = menu_ul.select_one("a[href*='current']")
                if current_issue_a:
                    relative_link = current_issue_a.get("href")
                    current_link = urllib.parse.urljoin(url, relative_link)

                    response = requests_retry_session().get(current_link, headers=headers, verify=False)
                    if response.status_code != 200:
                        raise Exception(f"Failed to fetch current issue URL: {current_link}")

                    soup_current = BeautifulSoup(response.content, "html.parser")

                    issue_toc_div = soup_current.find("div", class_="issue-toc")

                    if issue_toc_div:
                        div_elements = issue_toc_div.findAll("li")

                        Total_count = len(div_elements)
                        # print(f"Total number of articles:{Total_count}", "\n")

                        processed_titles = set()

                        for single_element in div_elements:
                            article_link, article_title = None, None
                            try:
                                article_title_elem = single_element.find("span", class_="highwire-cite-title")
                                article_link_elem = single_element.find("a", class_="highwire-cite-linked-title")

                                if article_title_elem and article_link_elem:
                                    article_title = article_title_elem.get_text(strip=True)

                                    if article_title not in processed_titles:
                                        processed_titles.add(article_title)
                                        article_link = urllib.parse.urljoin(url, article_link_elem.get("href"))

                                        day_month_info = soup_current.find("div", class_="panel-pane pane-custom pane-1 pane-page-title-suffix")

                                        day, month = "", ""
                                        if day_month_info:
                                            day_month_tag = day_month_info.find("p")
                                            if day_month_tag:
                                                day_month_text = day_month_tag.text.strip()
                                                match = re.match(r"(\d{2}) (\w+)", day_month_text)
                                                if match:
                                                    day = match.group(1)
                                                    month = match.group(2)

                                        volume_issue_info = single_element.find("div", class_="highwire-cite-metadata")
                                        volume, issue, article_no, doi, year = "", "", "", "", ""

                                        if volume_issue_info:
                                            volume = volume_issue_info.find("span", class_="highwire-cite-metadata-volume highwire-cite-metadata").text.strip()
                                            issue = volume_issue_info.find("span", class_="highwire-cite-metadata-issue highwire-cite-metadata").text.strip().replace("(", "").replace(")", "")
                                            article_no = volume_issue_info.find("span", class_="highwire-cite-metadata-pages highwire-cite-metadata").text.strip().split(";")[0].strip()
                                            doi = volume_issue_info.find("span", class_="highwire-cite-metadata-doi highwire-cite-metadata").text.strip().split(":")[1].strip()
                                            year = volume_issue_info.find("span", class_="highwire-cite-metadata-date highwire-cite-metadata").text.strip()
                                            year_match = re.search(r'\b\d{4}\b', year)
                                            if year_match:
                                                year = year_match.group(0)

                                        article_response = requests_retry_session().get(article_link, headers=headers, verify=False)
                                        if article_response.status_code != 200:
                                            raise Exception(f"Failed to fetch article URL: {article_link}")

                                        article_soup = BeautifulSoup(article_response.text, 'html.parser')
                                        pdf_links = article_soup.find("ul", class_="tabs inline panels-ajax-tab").find("li", class_="last").findAll("a", class_="panels-ajax-tab-tab")
                                        pdf_url = ""
                                        if pdf_links:
                                            last_pdf_link = pdf_links[-1]
                                            pdf_link = last_pdf_link.get("href")
                                            pdf_url = base_url + pdf_link

                                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                        if Check_duplicate.lower() == "true" and check_value:
                                            message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                            duplicate_list.append(message)
                                            print("Duplicate Article :", article_title)

                                        else:
                                            pdf_content = requests_retry_session().get(pdf_url, headers=headers, verify=False).content
                                            output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                            with open(output_fimeName, 'wb') as file:
                                                file.write(pdf_content)
                                            data.append(
                                                {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                 "ItemID": "",
                                                 "Identifier": "",
                                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                 "Article_No": article_no,
                                                 "Special Issue": "", "Page Range": "", "Month": month,
                                                 "Day": day,
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
                            common_function.sendCountAsPost(source_id, Ref_value, str(Total_count),
                                                            str(len(completed_list)),
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
                                common_function.attachment_for_email(source_id, duplicate_list, error_list,
                                                                     completed_list,
                                                                     len(completed_list), ini_path, attachment,
                                                                     current_date,
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
    Error_message = "General error occurred: " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
