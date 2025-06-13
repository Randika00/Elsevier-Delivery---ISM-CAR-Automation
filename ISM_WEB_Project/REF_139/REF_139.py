import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd
from googletrans import Translator

# Initialize the translator
translator = Translator()


def extract_details(text):
    year_match = re.search(r'(\d{4})年第', text)
    volume_match = re.search(r'第(\d+)卷', text)
    issue_match = re.search(r'第(\d+)期', text)
    doi_match = re.search(r'DOI:([^\s]+)', text)
    page_range_match = re.search(r'(\d{4},\d+\(\d+\)):(\d+-\d+)', text)

    year = year_match.group(1) if year_match else None
    volume = volume_match.group(1) if volume_match else None
    issue = issue_match.group(1) if issue_match else None
    doi = doi_match.group(1) if doi_match else None
    page_range = page_range_match.group(2) if page_range_match else None

    return year, volume, issue, doi, page_range

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

duplicate_list = []
error_list = []
completed_list=[]
data = []
attachment=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
Total_count=None
pdf_count=1
url_id="78711499"

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

ini_path= os.path.join(os.getcwd(),"REF_139.ini")
Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
out_excel_file = common_function.output_excel_name(current_out)
Ref_value="139"

url = "https://www.tiprpress.com/"
try:
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    TOC_path, TOC_name = common_function.output_TOC_name(current_out)
    with open(TOC_path, 'w', encoding='utf-8') as html_file:
        html_file.write(str(soup))
    first_page="https://www.tiprpress.com/"+soup.find("div",class_="bookbox").find("a").get("href")
    page_2 = requests.get(first_page, headers=headers)
    soup_2 = BeautifulSoup(page_2.content, 'html.parser')
    all_articles=soup_2.find("ul",class_="check_box").find_all("div",class_="slideTxtBox_list_title")
    Total_count = len(all_articles)
    print(f"Total number of articles:{Total_count}", "\n")
    for article in all_articles:
        Article_link = None
        try:
            Article_link = "https://www.tiprpress.com/"+article.find("a").get("href")
            title = article.find("a").get_text(strip=True)
            translated_title = translator.translate(title, src='zh-CN', dest='en').text
            Article_link_page = requests.get(Article_link, headers=headers)
            Article_link_soup = BeautifulSoup(Article_link_page.content, 'html.parser')
            span_tag =Article_link_soup.find('span', id='all_issue_position').get_text(strip=True)
            year, volume, issue, doi, page_range = extract_details(span_tag)
            print(f"Year: {year}, Volume: {volume}, Issue: {issue}, DOI: {doi}")
            pdf_link="https://www.tiprpress.com/"+Article_link_soup.find("div",class_="article_abstract_button_pdf").find("a").get("href")
            check_value, tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
            if Check_duplicate.lower() == "true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", translated_title)
            else:
                print("Original Article :", translated_title)
                pdf_content = requests.get(pdf_link, headers=headers).content
                output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                with open(output_fimeName, 'wb') as file:
                    file.write(pdf_content)
                print(f"Downloaded: {output_fimeName}")
                data.append({"Title": translated_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                pdf_count += 1
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                    write_file.write(Article_link + '\n')
        except Exception as error:
            message = f"Error link - {Article_link} : {str(error)}"
            error_list.append(message)
            print(error)

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
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass
except Exception as error:
    Error_message = "Error in the site :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

finally:
    subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
    error_file_path = os.path.join(current_out, 'download_details.html')
    with open(error_file_path, 'w', encoding='utf-8') as file:
        file.write(error_html_content)
    print("Error details file saved to:", error_file_path)