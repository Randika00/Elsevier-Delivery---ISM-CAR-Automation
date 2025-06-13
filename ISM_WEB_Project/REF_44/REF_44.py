import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

def print_bordered_message(message):
    border_length = len(message) + 4
    border = "-" * (border_length - 2)

    print(f"+{border}+")
    print(f"| {message} |")
    print(f"+{border}+")
    print()

def get_ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

def extract_info(html_string):
    # Define regex pattern for page range and DOI
    page_range_pattern = r"\d+-\d+"
    doi_pattern = r"10\.\d{4,}/[^\s]+"

    # Use regex to find matches
    page_range_match = re.search(page_range_pattern, html_string)
    doi_match = re.search(doi_pattern, html_string)

    # Extract page range and DOI if matches found
    page_range = page_range_match.group() if page_range_match else None
    doi = doi_match.group() if doi_match else None

    # Return extracted information
    return {
        "page_range": page_range,
        "doi": doi
    }
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
pdf_count=1
url_id="947344602"

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
Ref_value = "44"

url = "http://zh.zhhlzzs.com/EN/0254-1769/home.shtml"
try:
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    element=soup.find("div",class_="articles").find("div",class_="njq").get_text(strip=True)
    pattern = r"(\d{1,2})\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s*(\d{4}),\s*Volume\s*(\d+)\s*Issue\s*(\d+)"
    match = re.match(pattern,element)
    if match:
        day = match.group(1)
        month = match.group(2)
        year = match.group(3)
        volume = match.group(4)
        issue = match.group(5)
    else:
        print("No match day,month,year and volume found.")
    all_articles=soup.find_all("div",class_="wenzhang")
    Total_count = len(all_articles)
    print(f"Total number of articles:{Total_count}", "\n")
    article_index, article_check = 0, 0
    while article_index < len(all_articles):
        Article_count = article_index + 1
        Article_link, Article_title = None, None
        try:
            Article_link=all_articles[article_index].find("a",class_="biaoti").get("href")
            title=all_articles[article_index].find("a",class_="biaoti").get_text(strip=True)
            doi_string=all_articles[article_index].find("dd",class_="kmnjq").get_text(strip=True)
            page_range_pattern = r'(\d+-\d+)'
            doi_pattern = r'DOI:(\S+)'
            page_range_match = re.search(page_range_pattern, doi_string)
            if page_range_match:
                page_range = page_range_match.group(1)
            else:
                page_range = None
            doi_match = re.search(doi_pattern, doi_string)
            if doi_match:
                doi = doi_match.group(1)
            else:
                doi = None
            pdf_text = all_articles[article_index].find("dd", class_="zhaiyao").find("a", class_="txt_zhaiyao1", onclick=re.compile(r"lsdy1\('PDF','\d+'")).get('onclick')
            value_pattern = r"lsdy1\('PDF','(\d+)'"
            match = re.search(value_pattern, pdf_text)
            if match:
                value = match.group(1)
            else:
                value = None
            pdf_link = f"http://zh.zhhlzzs.com/CN/article/downloadArticleFile.do?attachType=PDF&id={value}"

            print_bordered_message(f"page_range: {page_range},DOI: {doi},pdf_link:{pdf_link}")
            if article_check == 0:
                print(get_ordinal_suffix(Article_count) + " article details have been scraped")
            check_value,tpa_id  = common_function.check_duplicate(doi, title, url_id, volume, issue)
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
                data.append({"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                pdf_count += 1
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                    write_file.write(Article_link + '\n')
                print(get_ordinal_suffix(Article_count) + " article is original article" + "\n" + "Article title:",title, "✅" + '\n')
            article_index, article_check = article_index + 1, 0
        except Exception as error:
            if article_check < 4:
                article_check += 1
            else:
                message = f"Error link - {Article_link} : {str(error)}"
                print_bordered_message(f"Download failed: {Article_title}")
                error_list.append(message)
                article_index, article_check = article_index + 1, 0
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
        common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)
    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass
except Exception as error:
        Error_message="Error in the site :"+str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)


