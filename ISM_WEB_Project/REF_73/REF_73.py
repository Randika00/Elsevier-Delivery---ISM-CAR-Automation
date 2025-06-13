import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

def extract_info(text):
    match = re.search(r'Vol\. (\d+) No\. (\d+) \((\d{4})\)', text)
    if match:
        volume = match.group(1)
        issue = match.group(2)
        year = match.group(3)
        return volume, issue, year
    else:
        return None, None, None

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

duplicate_list = []
error_list = []
completed_list=[]
data = []
Total_count=None
attachment=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
url_id="79732499"
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

ini_path= os.path.join(os.getcwd(),"REF_73.ini")
Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
out_excel_file = common_function.output_excel_name(current_out)
Ref_value="73"

url = "https://pjmhsonline.com/index.php/pjmhs"
try:
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    element=soup.find("div",class_="current_issue_title").get_text(strip=True)
    volume, issue, year = extract_info(element)
    all_articles=soup.find_all("div",class_="obj_article_summary")
    Total_count = len(all_articles)
    print(f"Total number of articles:{Total_count}", "\n")
    for article in all_articles:
        Article_link = None
        try:
            Article_link = article.find("h4", class_="title").find("a").get("href")
            title = article.find("h4", class_="title").find("a").get_text(strip=True)
            Article_link_page = requests.get(Article_link, headers=headers)
            Article_link_soup = BeautifulSoup(Article_link_page.content, 'html.parser')
            doi_string = Article_link_soup.find("span", class_="value").find("a").get_text(strip=True)
            parts = doi_string.split('/')
            doi = "/".join(parts[3:])
            pdf_url = Article_link_soup.find("ul", class_="value galleys_links").find("a").get("href")
            pdf_page = requests.get(pdf_url, headers=headers)
            pdf_soup = BeautifulSoup(pdf_page.content, 'html.parser')
            pdf_link = pdf_soup.find("header", class_="header_view").find("a", class_="download").get("href")
            check_value,tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
            if Check_duplicate.lower() == "true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", title)
            else:
                print("Original Article :", title)
                pdf_content = requests.get(pdf_link, headers=headers).content
                output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                with open(output_fimeName, 'wb') as file:
                    file.write(pdf_content)
                print(f"Downloaded: {output_fimeName}")
                scrape_message = f"{Article_link}"
                data.append({"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": "", "Month": "", "Day": "", "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
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

    try:
        common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                        str(len(duplicate_list)), str(len(error_list)))
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
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

finally:
    subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
    error_file_path = os.path.join(current_out, 'download_details.html')
    with open(error_file_path, 'w', encoding='utf-8') as file:
        file.write(error_html_content)
    print("Error details file saved to:", error_file_path)