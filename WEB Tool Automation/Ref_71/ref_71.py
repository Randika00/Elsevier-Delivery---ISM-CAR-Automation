import os
import pandas as pd
import requests
import re
import urllib3
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
import certifi

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url_id = "78063699"

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
    url = "http://epubs.icar.org.in/ejournal/index.php/IJAnS/issue/archive"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_71.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "71"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    cafile = certifi.where()

    response = requests.get(url, headers=headers, verify=False)
    current_link = BeautifulSoup(response.content, "html.parser").find("ul", class_="issues_archive").find("h2").find("a").get("href")

    response = requests.get(current_link, headers=headers, verify=False)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(response.text, "html.parser")

        div_element = soup.find("div", class_="sections").findAll("div", class_="obj_article_summary")

        Total_count = len(div_element)
        print(f"Total number of articles:{Total_count}", "\n")

        title_elements = soup.find_all("h3", class_="title")
        for idx, title_element in enumerate(title_elements, start=1):
            article_link, article_title = None, None
            try:
                article_title = title_element.text.strip()
                article_link = title_element.a['href']

                doi_element = title_element.find_next("span", class_="value")
                doi = ""
                if doi_element:
                    doi_link = doi_element.find("a", href=True)
                    if doi_link:
                        doi = doi_link['href'].split('/')[-1]
                        doi = "10.56093/" + doi

                meta_div = title_element.find_next("div", class_="meta")
                pages_div = meta_div.find("div", class_="pages")
                page_range = ""
                if pages_div:
                    page_range = pages_div.text.strip()

                issue_info = soup.find("li", class_="current").find("span").text.strip()

                volume, issue, year = re.findall(r'\d+', issue_info)

                last_page_link = title_element.find_next("ul", class_="galleys_links").find("a", class_="obj_galley_link pdf").get('href')

                last_response = requests.get(last_page_link, headers=headers, verify=False)
                last_soup = BeautifulSoup(last_response.text, "html.parser")

                pdf_url = last_soup.find("a", class_="download").get("href")

                check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", article_title)

                else:
                    pdf_content = requests.get(pdf_url, headers=headers, verify=False).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    data.append(
                        {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "",
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
