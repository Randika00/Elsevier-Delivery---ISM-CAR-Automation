import os
import pandas as pd
import requests
import re
import urllib3
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
import certifi

url_id = "79920799"

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
    url = "http://innovareacademics.in/journals/index.php/ijpps"
    base_url = "https://journals.innovareacademics.in/"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_138_01.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "138_01"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    current_link = BeautifulSoup(response.content, "html.parser").find("ul", class_="pkp_navigation_primary pkp_nav_list").findAll("li")[2].find("a").get("href")

    response = requests.get(current_link, headers=headers)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(response.text, "html.parser")

        div_element = soup.find("div", class_="sections").findAll("div", class_="obj_article_summary")

        Total_count = len(div_element)
        print(f"Total number of articles:{Total_count}", "\n")

        for single_element in div_element:
            article_link, article_title = None, None
            try:
                article_link_tag = single_element.find("div", class_="title")
                if article_link_tag:
                    article_title = article_link_tag.find("a").text.strip()
                    article_link = article_link_tag.find("a").get("href")

                    page_ranges = single_element.findAll("div", class_="pages")
                    doi_tags = single_element.findAll("ul", class_="galleys_links")
                    pdf_url_tags = single_element.findAll("ul", class_="galleys_links")

                    for page_range_tag, pdf_url_tag, doi_tag in zip(page_ranges, pdf_url_tags, doi_tags):

                        page_range = page_range_tag.text.strip()

                        pdf_url, doi = "", ""
                        if 'PDF' in pdf_url_tag.text:
                            last_page_link = pdf_url_tag.find("a", class_="obj_galley_link").get("href")
                            doi = doi_tag.find("a", class_="doi_link").text.strip()

                            last_response = requests.get(last_page_link, headers=headers)
                            last_soup = BeautifulSoup(last_response.text, "html.parser")

                            pdf_url = last_soup.find("header", class_="header_view").find("a", class_="download").get('href')

                        vol_issue_info = soup.find("h1").text.strip()
                        match = re.search(r'Vol (\d+), Issue (\d+), (\d+)', vol_issue_info)
                        volume, issue, year = "", "", ""
                        if match:
                            volume = match.group(1)
                            issue = match.group(2)
                            year = match.group(3)

                        article_response = requests.get(article_link, headers=headers)
                        if article_response.status_code == 200:
                            article_soup = BeautifulSoup(article_response.text, 'html.parser')

                            month_info = article_soup.find("section", class_="sub_item")
                            full_month = ""
                            if month_info:
                                month_text = month_info.find("div", class_="value").text.strip()
                                date_obj = datetime.strptime(month_text, "%d-%m-%Y")
                                full_month = date_obj.strftime("%B")

                            orc_tag = article_soup.find("ul", class_="authors").find("span", class_="orcid")
                            orc_id = ""
                            if orc_tag:
                                orc_id = orc_tag.find("a").get("href").replace("https://orcid.org/", "")

                            # orc_tags = article_soup.find("ul", class_="authors").findAll("span", class_="orcid")
                            # for orc_tag in orc_tags:
                            #     orc_id_link = orc_tag.find("a").get("href")
                            #     print(f"ORCID: {orc_id_link}")

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
                                     "Volume": volume, "Issue": issue, "Supplement": "", "Part": "", "OCR_ID": orc_id,
                                     "Special Issue": "", "Page Range": page_range, "Month": full_month, "Day": "",
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

