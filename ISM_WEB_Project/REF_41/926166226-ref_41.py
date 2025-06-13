import requests
from bs4 import BeautifulSoup
import os
import re
import urllib.parse
from urllib.parse import urlparse
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

Total_count=None
duplicate_list = []
error_list = []
completed_list=[]
data = []
attachment=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
url_id="926166226"
pdf_count=1

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

current_datetime = datetime.now()
current_date = str(current_datetime.date())
current_time = current_datetime.strftime("%H:%M:%S")

ini_path = os.path.join(os.getcwd(), "Info.ini")

Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
out_excel_file = common_function.output_excel_name(current_out)
Ref_value = "41"

url = "https://www.academicmed.org/current-issue"
try:
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    input_string =soup.find("p",class_="current_issue_title lead").get_text()
    pattern = r"Year\s*:\s*(\d+)\s*–\s*Volume:\s*(\d+)\s*Issue:\s*(\d+)"
    matches = re.search(pattern, input_string)
    if matches:
        year = matches.group(1)
        volume = matches.group(2)
        issue = matches.group(3)
    all_articles=soup.find_all("div",class_="media-body")
    Total_count = len(all_articles)
    print(f"Total number of articles:{Total_count}", "\n")
    for article in all_articles:
        Article_link = None
        try:
            title_link = article.find("div", class_="WrpMediaCnt").find("a")
            if title_link:
                title = title_link.get_text(strip=True)
                link = "https://www.academicmed.org"+title_link.get('href')
                parsed_url = urlparse(link)
                scheme = parsed_url.scheme
                netloc = parsed_url.netloc
                path = parsed_url.path
                encoded_path = "/".join(map(urllib.parse.quote, path.split("/")))
                Article_link = f"{scheme}://{netloc}{encoded_path}"
                page_range_span = article.find("div",class_="row").find("p", style="font-size:15px").find("span")
                if page_range_span:
                    page_range= page_range_span.get_text(strip=True).replace("Page No:", "").strip()
                doi= article.find("div", class_="WrpMediaCnt").find("p").get_text(strip=True).rsplit('doi.org/',1)[-1]
                check_value,tpa_id  = common_function.check_duplicate(doi, title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", title)
                else:
                    print("Original Article :", title)
                    pdf_content = requests.get(Article_link, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    print(f"Downloaded: {output_fimeName}")
                    data.append({"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                 "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                                 "URL":Article_link , "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(Article_link)
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

        except Exception as error:
            message = f"Error link - {Article_link} : {str(error)}"
            error_list.append(message)
    try:
        common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),str(len(duplicate_list)), str(len(error_list)))
    except Exception as error:
        message = str(error)
        error_list.append(message)
    if str(Email_Sent).lower() == "true":
        attachment_path = out_excel_file
        if os.path.isfile(attachment_path):
            attachment = attachment_path
        else:
            attachment = None
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)
    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass
except Exception as error:
    Error_message = "Error in the site :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path,attachment, current_date, current_time, Ref_value)
