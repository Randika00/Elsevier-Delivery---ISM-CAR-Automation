import os
import pandas as pd
import requests
import re
import urllib3
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
import certifi

url_id = "925313428"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

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
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')


try:
    url = "https://ijettjournal.org/articles"
    base_url = "https://ijettjournal.org/"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_147.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "147"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = requests.get(url, headers=headers)

    relative_url = BeautifulSoup(response.content, "html.parser").find("div", class_="container").find("div", class_="col-sm morebtn").find("a", class_="articles").get("href")

    current_link = base_url + relative_url
    response = requests.get(current_link, headers=headers)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(response.text, "html.parser")

        all_articles = soup.find("tbody").findAll("td", style="width: 47px;")

        Total_count = len(all_articles)
        # print(f"Total number of articles: {Total_count}", "\n")

        table_element = soup.find("table", class_="volume volume71-issue-2")

        if table_element:
            rows = table_element.findAll("tr")
            for single_ele in rows:
                article_link, article_title = None, None
                try:
                    p_elements = single_ele.findAll("p")
                    for p in p_elements:
                        article = p.find("a")
                        if article:
                            article_url = article.get("href")
                            if article_url:
                                article_link = base_url + article_url

                                article_title = p.find("a").text.strip()

                                vol_issue_day_info = soup.find("div", class_="page-header").find("h2")
                                volume, issue, month, year = "", "", "", ""
                                if vol_issue_day_info:
                                    vol_issue_day_text = vol_issue_day_info.get_text(strip=True)
                                    match = re.search(r'Volume(\d+)\sIssue(\d+)\s(\w+)\s(\d{4})', vol_issue_day_text)
                                    if match:
                                        volume = match.group(1)
                                        issue = match.group(2)
                                        month = match.group(3)
                                        year = match.group(4)

                                article_response = requests.get(article_link, headers=headers)
                                if article_response.status_code == 200:
                                    article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                    doi_element = article_soup.find("a", href=re.compile(r"^https://doi.org/"))
                                    doi = ""
                                    if doi_element:
                                        doi = doi_element.get_text(strip=True)

                                    pdf_url_tag = article_soup.find("a", href=re.compile(r"\.pdf$"))
                                    pdf_url = ""
                                    if pdf_url_tag:
                                        pdf_link = pdf_url_tag.get("href")
                                        pdf_url = base_url + pdf_link

                                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)

                                    if Check_duplicate.lower() == "true" and check_value:
                                        message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                        duplicate_list.append(message)
                                        print("Duplicate Article :", article_title)

                                    else:
                                        pdf_content = requests.get(pdf_url, headers=headers).content
                                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                        with open(output_fimeName, 'wb') as file:
                                            file.write(pdf_content)
                                        data.append(
                                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                             "Identifier": "",
                                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                             "Special Issue": "", "Page Range": "", "Month": month, "Day": "",
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
                common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
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
                    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
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
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)





