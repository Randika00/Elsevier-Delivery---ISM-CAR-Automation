import os
import pandas as pd
import requests
import re
import urllib3
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
import certifi

url_id = "657092802"

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
doi = None
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
    url = "https://geomednews.com/currentissue.html"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_144.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "144"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    div_element = soup.find("div", class_="u_1657004938 small-12 dmRespCol large-8 medium-8").findAll("p", {"style":"text-align: left;"})

    Total_count = len(div_element)
    # print(f"Total number of articles:{Total_count}", "\n")

    for single_element in div_element:
        article_link, article_title = None, None
        try:

            article_link_tag = single_element.find("a")
            if article_link_tag:
                article_link = article_link_tag.get('href')
                article_title_tag = article_link_tag.find("strong")
                if article_title_tag:
                    article_title = article_title_tag.text.strip()
                else:
                    print("Article title tag not found.")

                text_nodes = single_element.stripped_strings
                page_range = list(text_nodes)[-1]

                month_year_info = soup.find("p", class_="text-align-center m-size-25 size-36").findAll("span", class_="m-font-size-25 font-size-36")
                month, year = "", ""
                if month_year_info:
                    month_span = month_year_info[0]
                    year_span = month_year_info[-1]

                    month = month_span.text.strip() if 'Times New Roman' in month_span.get('style', '') else None
                    year = year_span.text.strip() if 'Times New Roman' in year_span.get('style', '') else None

                volume_issue_info = soup.find("div", class_="u_1855227140 dmRespCol small-12 medium-12 large-12").findAll("p", class_="m-size-8 text-align-center size-12")
                volume, issue = "", ""
                if volume_issue_info:
                    vol_issue_span = volume_issue_info[0].find("span", class_="font-size-12 m-font-size-8")
                    if vol_issue_span:
                        vol_issue_text = vol_issue_span.text.strip()
                        match = re.search(r'VOL\.\s*(\d+)\s+No\.\s*(\d+)', vol_issue_text)
                        if match:
                            volume = match.group(1)
                            issue = match.group(2)

                pdf_link_tag = single_element.find("a")
                pdf_url = ""
                if pdf_link_tag:
                    pdf_url = pdf_link_tag.get('href')

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
                        {"Title": article_title, "DOI": "", "Publisher Item Type": "", "ItemID": "",
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