import os
import pandas as pd
import requests
import re
import urllib3
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
import certifi

url_id = "76464199"

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
    url = "https://www.jneurosci.org/content/by/year"
    base_url = "https://www.jneurosci.org"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_143.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "143"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = requests.get(url, headers=headers)

    relative_url = BeautifulSoup(response.content, "html.parser").find("div", class_="archive-issue-list").find("ul", class_="issue-month-detail").find("div", class_="highwire-cite-metadata").find("a", class_="hw-issue-meta-data").get("href")

    current_link = base_url + relative_url
    response = requests.get(current_link, headers=headers)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(response.text, "html.parser")

        all_articles = soup.find("div", class_="issue-toc").findAll("div", class_="toc-citation")

        Total_count = len(all_articles)
        print(f"Total number of articles:{Total_count}", "\n")

        div_element = soup.find("div", class_="issue-toc").findAll("ul", class_="toc-section")

        for single_ele in div_element:
            article_link, article_title = None, None
            try:

                first_article = single_ele.findAll("li", class_="toc-item")
                for article in first_article:
                    articles = article.find("a", class_="highwire-cite-linked-title").get("href")
                    article_link = base_url + articles

                    article_title = article.find("a", class_="highwire-cite-linked-title").find("span", class_="highwire-cite-title").text.strip()

                    month_info = article.find("div", class_="highwire-cite-metadata").find("span", class_="highwire-cite-metadata-date highwire-cite-metadata")
                    day, month, year = "", "", ""
                    if month_info:
                        month_text = month_info.get_text(strip=True)
                        day, month, year = re.findall(r'\b(\d+)\s(\w+)\s(\d{4})\b', month_text)[0]

                    volume_info = article.find("div", class_="highwire-cite-metadata").find("span", class_="highwire-cite-metadata-volume highwire-cite-metadata")
                    volume = ""
                    if volume_info:
                        volume = volume_info.text.strip()

                    issue_info = article.find("div", class_="highwire-cite-metadata").find("span", class_="highwire-cite-metadata-issue highwire-cite-metadata")
                    issue = ""
                    if issue_info:
                        issue = issue_info.text.strip().strip('()')

                    identifier_info = article.find("div", class_="highwire-cite-metadata").find("span", class_="highwire-cite-metadata-pages highwire-cite-metadata")
                    identifier = ""
                    if identifier_info:
                        identifier = identifier_info.text.strip().strip(';')

                    doi_info = article.find("div", class_="highwire-cite-metadata").find("span", class_="highwire-cite-metadata-doi highwire-cite-metadata")
                    doi = ""
                    if doi_info:
                        doi = doi_info.text.strip().replace("https://doi.org/", "")

                    article_response = requests.get(article_link, headers=headers)
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')

                        pdf_url_tag = article_soup.find("div", class_="item-list").find("li", class_="last")
                        pdf_url = ""
                        if pdf_url_tag:
                            pdf_link = pdf_url_tag.find("a").get("href")
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
                                 "Identifier": identifier,
                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                 "Special Issue": "", "Page Range": "", "Month": month, "Day": day,
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
