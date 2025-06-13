import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd
import PyPDF2
import io

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}


def extract_doi_from_pdf_link(pdf_url):
    try:
        # Step 1: Download the PDF into memory
        response = requests.get(pdf_url)
        response.raise_for_status()  # Check if the request was successful
        pdf_content = io.BytesIO(response.content)  # Load content into memory

        # Step 2: Extract text only from the first page of the PDF content
        reader = PyPDF2.PdfReader(pdf_content)
        text = ""
        if len(reader.pages) > 0:
            text = reader.pages[0].extract_text()

        # Step 3: Use regex to find the DOI
        pattern = re.compile(r'DOI\s*[:：]\s*(.+)', re.UNICODE)
        match = re.search(pattern, text)

        if match:
            doi = match.group(1).replace(" ", "")
            print(f"Extracted DOI: {doi}")
            return doi
        else:
            doi=""
            print(f"Extracted DOI: {doi}")
            return ""
    except Exception as e:
        return f"Error extracting DOI: {str(e)}"

def get_token(url):
    response = requests.get(url,headers=headers)
    cookie=response.cookies
    print(cookie)
    token=cookie.get("JSESSIONID").replace("-","")
    return token

def get_soup(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

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

duplicate_list = []
error_list = []
completed_list = []
attachment = None
url_id = None
current_date = None
current_time = None
Ref_value = None
ini_path = None
Total_count = None

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

try:
    with open('urlDetails.txt', 'r', encoding='utf-8') as file:
        url_list = file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\" : " + str(error)
    print_bordered_message(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

chinese_url="http://www.zwbhxb.cn/ch/index.aspx"
url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        print_bordered_message("Process started...")
        print("This may take some time. Please wait..........")
        url, url_id = url_list[url_index].split(',')
        print(f"Executing this {url}")

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "REF_3656.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "3656"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1
        url_value = url.split('/')[-3]

        soup = get_soup(url)

        Cn_soup=get_soup(chinese_url)
        combine_soup = str(soup) + str(Cn_soup)
        TOC_path, TOC_name = common_function.output_TOC_name(current_out)
        with open(TOC_path, 'w', encoding='utf-8') as html_file:
            html_file.write(combine_soup)

        All_articles =soup.find_all('tr', class_='article_name_value')
        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}", "\n")
        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index + 1
            Article_link, Article_title = None, None
            try:
                Article_link = "http://www.zwbhxb.cn/zbxben/ch/"+All_articles[article_index].find("td", align="left").find("a").get('href')
                Article_title = All_articles[article_index].find("td", align="left").find("a").text.strip()

                meta_text=All_articles[article_index].find("td", align="left").text.strip()
                pattern = r"(\d{4}),Vol\.(\d+)\((\d+)\)"
                match = re.search(pattern, meta_text)

                if match:
                    year = match.group(1)
                    volume = match.group(2)
                    issue = match.group(3)
                    print(f"Year: {year}, Volume: {volume}, Issue: {issue}")
                else:
                    print("No match found")

                pdf_page_soup = get_soup(Article_link)
                page_range_text = pdf_page_soup.find("span", id="ReferenceText").get_text(strip=True)
                try:
                    pattern = r"(\d+-\d+)"
                    match = re.search(pattern, page_range_text)
                    page_range = match.group(1) if match else ""

                    print(f"Page Range: '{page_range}'")
                except Exception as e:
                    page_range=""
                    print(f"An error occurred: {e}")

                pdf_link = "http://www.zwbhxb.cn/zbxben/ch/"+All_articles[article_index].find("td", align="left").find_all("a")[-1].get('href')
                print(pdf_link)

                try:
                    doi = extract_doi_from_pdf_link(pdf_link)
                    print(doi)
                except Exception as e:
                    doi=""



                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print_bordered_message(f"Duplicate Article: {Article_title}")
                else:
                    session = requests.Session()
                    retries = 0
                    max_retries = 5
                    download_successful = False

                    while retries < max_retries and not download_successful:
                        response = session.get(pdf_link, headers=headers)
                        pdf_content = response.content

                        output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_fileName, 'wb') as file:
                            file.write(pdf_content)

                        if os.path.getsize(output_fileName) > 0:
                            print(f"Downloaded: {output_fileName}")
                            download_successful = True
                        else:
                            retries += 1
                            print(f"Retrying download... Attempt {retries}/{max_retries}")

                    if download_successful:
                        data.append(
                            {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                             "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print(get_ordinal_suffix(Article_count)+" article is original article" +"\n"+"Article title:", Article_title,"✅"+ '\n')

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
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)), str(len(error_list)))
        except Exception as error:
            message = str(error)
            error_list.append(message)

        if str(Email_Sent).lower() == "true":
            attachment_path = out_excel_file
            if os.path.isfile(attachment_path):
                attachment = attachment_path
            else:
                attachment = None
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list, len(completed_list), url_id, Ref_value, attachment, current_out)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the site:" + str(error)
            print_bordered_message(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list, len(completed_list), url_id, Ref_value, attachment, current_out)
            url_index, url_check = url_index + 1, 0
