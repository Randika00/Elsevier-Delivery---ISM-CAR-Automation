import re
import requests
import json
from bs4 import BeautifulSoup
import os
import common_function
import pandas as pd
from datetime import datetime


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

month_mapping = {
    "Jan.": "January", "Feb.": "February", "Mar.": "March", "Apr.": "April",
    "May": "May", "Jun.": "June", "Jul.": "July", "Aug.": "August",
    "Sep.": "September", "Oct.": "October", "Nov.": "November", "Dec.": "December"
}
def get_token(url):
    response = requests.get(url, headers=headers)
    cookie = response.cookies
    token = cookie.get("wkxt3_csrf_token").replace("-", "")
    return token


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

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
statusCode = None

try:
    with open('urlDetails.txt', 'r', encoding='utf-8') as file:
        url_list = file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\": " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        pass
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')

url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        url, url_id = url_list[url_index].split(',')
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print_bordered_message("🔍 Scraping in progress... Continuing with ID: " + url_id)
            ini_path = os.path.join(os.getcwd(), "REF_534.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "534"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        attachment = None
        pdf_count = 1

        soup=get_soup(url)
        en_href="http://hdlgc.xml-journal.net"+soup.find("li",type="english").find("a").get("href")
        en_soup=get_soup(en_href)
        combine_soup = str(soup) + str(en_soup)
        TOC_path, TOC_name = common_function.output_TOC_name(current_out)
        with open(TOC_path, 'w', encoding='utf-8') as html_file:
            html_file.write(str(combine_soup))

        curren_issue_link="http://hdlgc.xml-journal.net"+en_soup.find("li",type="currentIssue_en").find("a").get("href")
        curren_issue_soup=get_soup(curren_issue_link)
        date_time_meta=curren_issue_soup.find("h2",class_="journalIssue text-center commontit").find("p").get_text(strip=True)
        match = re.search(r"(\d{4}),\s*Volume\s*(\d+),\s*Issue\s*(\d+)", date_time_meta)

        if match:
            year = match.group(1)
            volume = match.group(2)
            issue = match.group(3)

            print(f'year="{year}", volume="{volume}", issue="{issue}"')
        else:
            print("No match found.")
        All_articles = curren_issue_soup.find_all("div",class_="article-list-right")
        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index + 1
            Article_link, Article_title = None, None
            try:
                Article_link = All_articles[article_index].find("a").get("href")
                Article_title = All_articles[article_index].find("a").get_text(strip=True)
                page_range_text=All_articles[article_index].find("div", class_="article-list-time").find("font").get_text(strip=True)
                match = re.search(r":\s*([\d\-]+)\.", page_range_text)

                if match:
                    page_range = match.group(1)
                    print(f'page_range="{page_range}"')
                doi = All_articles[article_index].find("div", class_="article-list-time").find("a").get_text(strip=True)

                pdf_page_soup=get_soup(Article_link)
                month_text=pdf_page_soup.find("div",class_="ii-pub-date").get_text(strip=True)
                match = re.search(r"([A-Za-z]{3,4}\.)\s*\d{4}", month_text)

                if match:
                    abbreviated_month = match.group(1).strip()  # Extract month abbreviation
                    full_month = month_mapping.get(abbreviated_month, "Unknown")  # Get full month name
                    print(f'month="{full_month}"')

                links = pdf_page_soup.find("div",class_="pdf-xml clearfix")
                pdf_tag = links.find('a', onclick=lambda x: 'downloadpdf' in x if x else False)
                if pdf_tag:
                    onclick_value = pdf_tag.get('onclick')
                    pdf_id = onclick_value.split("'")[1]
                    pdf_link = f"http://hdlgc.xml-journal.net/article/exportPdf?id={pdf_id}&language=en"
                    xml_link=f"http://hdlgc.xml-journal.net/article/exportXML?ids={pdf_id}&downType=XML&language=en"
                    print(f'id="{pdf_id}"')

                if article_check == 0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")

                print_bordered_message(f"Month:{full_month},page_range: {page_range},DOI: {doi},pdf_link:{pdf_link}, XML_link:{xml_link}")

                check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID: {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count) + " article is a duplicate\nArticle title: " + Article_title + "📚\n")

                else:
                    print("Wait until the XML is downloaded")
                    response = requests.get(xml_link)
                    xml_content = response.content

                    if response.status_code == 200:
                        xml_filename = os.path.join(current_out, f"{pdf_count}.xml")
                        with open(xml_filename, 'wb') as file:
                            file.write(xml_content)
                        print(f"XML file downloaded successfully as {pdf_count}.xml")
                    else:
                        print(f"Failed to download the XML file. Status code: {response.status_code}")
                    print("Wait until the PDF is downloaded")
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



                    print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")
                    if download_successful:
                        data.append({
                            "Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                            "Identifier": "", "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                            "Special Issue": "", "Page Range": page_range, "Month": full_month, "Day": "",
                            "Year": year, "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf","XML File Name": f"{pdf_count}.xml",
                            "user_id": user_id,"TOC": TOC_name
                        })

                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print(get_ordinal_suffix(Article_count) + " article is original\nArticle title: " + Article_title + "✅\n")

                        if Article_link not in read_content:
                            with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 0:
                    article_check += 1
                else:
                    message = f"{Article_link} - Error in for {Article_title}: [{str(error)}]"
                    print(get_ordinal_suffix(Article_count) + " article could not be downloaded due to an error\nArticle title: " + Article_title + "❌\n")
                    error_list.append(message)
                    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)
                    article_index, article_check = article_index + 1, 0




        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),str(len(duplicate_list)), str(len(error_list)))
        except Exception as error:
                error_list.append(f"Failed to send post request: {str(error)}")
                print(error)
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)

        try:
            if str(Email_Sent).lower() == "true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)
        except Exception as error:
            message = f"Failed to send email: {str(error)}"
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value, attachment,current_out)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        print_bordered_message("Scraping has been successfully completed for ID: " + url_id)

        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 0:
            url_check += 1
        else:
            try:
                url_index, url_check = url_index + 1, 0
                error_messages = {
                    200: "Server error: Unable to find HTML content",
                    400: "Error in the site: 400 Bad Request",
                    401: "Error in the site: 401 Unauthorized",
                    403: "Error in the site: 403 Forbidden",
                    404: "Error in the site: 404 Page not found!",
                    408: "Error in the site: 408 Request Timeout",
                    500: "Error in the site: 500 Internal Server Error"
                }
                Error_message = error_messages.get(statusCode)

                if Error_message is None:
                    Error_message = "Error in the site: " + str(error)

                print(Error_message, "\n")
                error_list.append(Error_message)
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list), ini_path, attachment, current_date,
                                                     current_time, Ref_value)

            except Exception as error:
                message = f"Failed to send email: {str(error)}"
                print(message)
                common_function.email_body_html(current_date, current_time, duplicate_list, error_list,
                                                completed_list, len(completed_list), url_id, Ref_value,
                                                attachment, current_out)
                error_list.append(message)
