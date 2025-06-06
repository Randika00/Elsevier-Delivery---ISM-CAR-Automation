import requests
from bs4 import BeautifulSoup
import re
import os
import common_function
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

USERNAME = "bd-scm@elsevier.com"
PASSWORD = "7fxzXsUR"

source_id = "78096999"
duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
ini_path = None
doi = None

def get_response_with_retry(url, headers, session):
    response = session.get(url, headers=headers, timeout=30)
    return response

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

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
        read_content = []

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://www.chebsbornik.ru"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_545.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "545"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers, session=session)
            current_link = BeautifulSoup(response.content, "html.parser").find("div", class_="col-sm-9 archivecont").find("div", class_="thumbnail").find("a").get("href")

            response = get_response_with_retry(current_link, headers=headers, session=session)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                div_element = soup.find("ul", class_="articles-list")
                if div_element:
                    div_element = div_element.findAll("li")
                else:
                    print("No articles found.")
                    continue

                Total_count = len(div_element)
                # print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("h5")
                        if article_title_div:
                            article_title = article_title_div.find("a").text.strip() if article_title_div.find("a") else "No Title"
                            article_link = article_title_div.find("a").get('href') if article_title_div.find("a") else None

                            month_volume_issue_info = soup.find("div", class_="col-sm-8 col-sm-offset-2")
                            if month_volume_issue_info:
                                date_text = month_volume_issue_info.find("div", class_="releasedate")
                                if date_text:
                                    date_text = date_text.text.strip()
                                    month = date_text.split("/")[0].split()[0]
                                    year = date_text.split()[-1]
                                else:
                                    print("Month and Year not found.")
                                    month, year = None, None

                                vol_issue_text = month_volume_issue_info.find("h1").text.strip()
                                vol_issue_match = re.search(r"Vol\.\s*(\d+)\((\d+)\)", vol_issue_text)

                                if vol_issue_match:
                                    volume, issue = vol_issue_match.groups() if vol_issue_match else ""
                                else:
                                    print("Volume and issue not found.")
                                    volume, issue = None, None

                                article_response = get_response_with_retry(article_link, headers=headers, session=session)
                                if article_response.status_code == 200:
                                    article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                    login_text = article_soup.find("div", class_="col-sm-12 fullarticle").find("div", id="login-inpage") if article_soup.find("div", class_="col-sm-12 fullarticle") else None
                                    if login_text:
                                        login_data = {
                                            "email": USERNAME,
                                            "password": PASSWORD,
                                            "submit": "Login now to read the full article"
                                        }
                                        login_response = session.post(article_link, headers=headers, data=login_data)

                                        if "logout" in login_response.text.lower() or login_response.status_code == 200:
                                            print("Login successful!")
                                            article_response = get_response_with_retry(article_link, headers=headers, session=session)
                                            if article_response.status_code == 200: 
                                                article_soup = BeautifulSoup(article_response.text, "html.parser")
                                        else:
                                            print("Login failed. Check credentials or site restrictions.")
                                    else:
                                        print("No login required. Proceeding with article content.")

                                    pdf_container = article_soup.find("div", class_="col-sm-12 text-right")
                                    pdf_link = ""
                                    if pdf_container:
                                        pdf_link_tag = pdf_container.find("a")
                                        if pdf_link_tag and pdf_link_tag.get("href"):
                                            pdf_link = pdf_link_tag["href"]
                                        else:
                                            print("PDF link not found.")
                                    else:
                                        print("No PDF container found.")

                                    if pdf_link:
                                        pdf_content = get_response_with_retry(pdf_link, headers=headers, session=session).content
                                        output_filename = os.path.join(current_out, f"{pdf_count}.pdf")
                                        with open(output_filename, 'wb') as file:
                                            file.write(pdf_content)
                                        data.append(
                                            {"Title": article_title, "DOI": "", "Publisher Item Type": "",
                                             "ItemID": "",
                                             "Identifier": "",
                                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                             "Special Issue": "", "Page Range": "", "Month": month,
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
    Error_message = "Error in the urlDetails.txt file: " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
