print("This is Ref_275")

import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# import undetected_chromedriver as uc
# import chromedriver_autoinstaller as chromedriver
# chromedriver.install()
from bs4 import BeautifulSoup
import re
import certifi
import os
import sys
from datetime import datetime
import common_function
import pandas as pd
from PyPDF2 import PdfReader
import requests


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None

def extract_doi_and_page_range(text):
    parts = text.split()
    page_range = None
    doi = None

    for i, part in enumerate(parts):

        if '-' in part and part.replace('-', '').replace('.', '').isdigit():
            page_range = part.rstrip('.,')

        if part.lower().startswith('doi:'):
            doi = part.split(':', 1)[1]
            if i + 1 < len(parts):
                doi += parts[i + 1]

    return {
        "Page Range": page_range,
        "DOI": doi
    }

try:
    print("Process started...")
    print("This may take sometime.Please wait..........")

    try:
        with open('urlDetails.txt', 'r', encoding='utf-8') as file:
            url_list = file.read().split('\n')
    except Exception as error:
        Error_message = "Error in the \"urlDetails\" : " + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                             len(completed_list),
                                             ini_path, attachment, current_date, current_time, Ref_value)

    for i, url_url_id in enumerate(url_list):

        try:
            url, url_id = url_url_id.split(',')
            print(f"Executing this {url}")
            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)

            data = []
            pdf_count = 1
            Ref_value = "275"
            url_value = url.split('/')[-2]
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)


            response = requests.get(url, headers=headers, timeout=50,allow_redirects=True)
            current_soup = BeautifulSoup(response.content, 'html.parser')

            TOC_path, TOC_name = common_function.output_TOC_name(current_out)
            with open(TOC_path, 'w', encoding='utf-8') as html_file:
                html_file.write(str(current_soup))

            articles = current_soup.find("div",class_="cen_k2").findAll("ul")
            pdf_list = []
            for article in articles:
                Article_link = article.find("li", class_="width").find('a')["href"]
                Article_link = "http://www.cjmit.com/cjmit/ch/" +Article_link

                response2 = requests.get(Article_link, headers=headers, timeout=50, allow_redirects=True)
                current_soup2 = BeautifulSoup(response2.content, 'html.parser')

                page_range = current_soup2.find("span", id="ReferenceText").text.split(":")[-1]
                Article_title = current_soup2.find("span", id="EnTitle").text
                if not Article_title == "":
                    print(Article_title)
                else:
                    Article_title = current_soup2.find("span", id="FileTitle").text
                    print(Article_title)
                DOI = current_soup2.find("span", id="DOI").text

                date_volume = current_soup2.find("span", id="ReferenceText").text.split(":")[-2].split(",")
                year = date_volume[-2]
                volume, issue = date_volume[-1].split("(")[0], date_volume[-1].split("(")[1][:-1]

                Pdf_link = current_soup2.find("span",id = "URL").find("a")["href"]
                Pdf_link  = "http://www.cjmit.com/cjmit/ch/reader/"+Pdf_link

                check_value, tpa_id = common_function.check_duplicate(DOI, Pdf_link, url_id, volume, issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Pdf_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Pdf_link)
                else:
                    if Article_title not in pdf_list:
                        response_2 = requests.get(Pdf_link, headers=headers, timeout=50,verify=False)
                        pdf_content = response_2.content
                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_fimeName, 'wb') as file:
                            file.write(pdf_content)

                        data.append(
                            {"Title": Article_title, "DOI": DOI,
                             "Publisher Item Type": "",
                             "ItemID": "",
                             "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "",
                             "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "",
                             "Day": "",
                             "Year": year,
                             "URL": Article_link,
                             "SOURCE File Name": f"{pdf_count}.pdf",
                             "user_id": user_id,
                             "TOC":TOC_name})

                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        print(f"Downloaded the PDF file {pdf_count}")
                        pdf_count += 1
                        completed_list.append(Pdf_link)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Pdf_link + '\n')
                        pdf_list.append(Article_title)
                        print("###################################")

            if str(Email_Sent).lower() == "true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list), ini_path, attachment, current_date,
                                                     current_time, Ref_value)

            sts_file_path = os.path.join(current_out, 'Completed.sts')
            with open(sts_file_path, 'w') as sts_file:
                pass

        except Exception as error:
            Error_message = f"Error in the site: {error}"
            print(Error_message, "\n")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except:
    Error_message = "Error in the main process :"

    error_list.append(str(Error_message))
    log_file_path = os.path.join('log.txt')
    with open(log_file_path, 'w') as log_file:
        log_file.write(str(Error_message) + '\n')