import re
import urllib.request
import urllib.parse
import urllib.error
import requests
import urllib3
from bs4 import BeautifulSoup
import os
import common_function
import pandas as pd
from datetime import datetime
import ssl

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_soup(url):
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def extract_volume_and_year(text):
    volume_pattern = r'No\. (\d+)'
    year_pattern = r'\b(\d{4})\b'

    volume_match = re.search(volume_pattern, text)
    year_match = re.search(year_pattern, text)

    volume = volume_match.group(1) if volume_match else ""
    year = year_match.group(1) if year_match else ""

    return volume, year

def get_ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "revistas.uva.es",
    "Referer": "https://revistas.uva.es/index.php/invehisto/issue/view/390",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

duplicate_list = []
error_list = []
completed_list = []
Total_count = None
attachment = None
url_id = None
current_date = None
current_time = None
Ref_value = None
ini_path = None

try:
    with open('urlDetails.txt', 'r', encoding='utf-8') as file:
        url_list = file.read().strip().split('\n')
except Exception as error:
    Error_message = f"Error in the \"urlDetails\": {str(error)}"
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().strip().split('\n')
except FileNotFoundError:
    open('completed.txt', 'w', encoding='utf-8').close()
    read_content = []

url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        url, url_id = url_list[url_index].split(',')

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            ini_path = os.path.join(os.getcwd(), "REF_219.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "219"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1
        print(url_id)
        if url_id != "923277225":
            current_issue_soup = get_soup(url)
            current_issue_href = current_issue_soup.find("div", class_="pkp_navigation_primary_wrapper").find("ul",class_="pkp_navigation_primary pkp_nav_list").find("li").find("a").get("href")
            current_eng_soup=get_soup(current_issue_href)
            current_issue_href_eng = current_eng_soup.find("li", class_="locale_en_US").find("a").get('href')
            soup = get_soup(current_issue_href_eng)
        else:
            if 'url' in locals():
                soup = get_soup(url)
            else:
                raise ValueError("current_issue_href_eng is not defined")


        texts = soup.find("div", class_="page page_issue").find("h1").get_text(strip=True).split(':')[0].strip()

        volume, year = extract_volume_and_year(texts)
        print(f"Volume: {volume}, Year: {year}")

        All_articles = soup.findAll("div", class_="obj_article_summary")

        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index + 1
            Article_link, Article_title = None, None
            try:
                Article_title = All_articles[article_index].find("div", class_="title").text.strip()
                Article_link = All_articles[article_index].find("div",class_="title").find("a").get('href')
                try:
                    page_range = All_articles[article_index].find("div", class_="pages").text.strip()
                except Exception as e:
                    page_range = ""

                article_details = get_soup(Article_link)

                # Article_title =article_details.find("h1", class_="page_title").get_text(strip=True)
                # print(Article_title)
                try:
                    doi_text = article_details.find("span", class_="value").get_text(strip=True)
                    doi_pattern = r"10\.\d{4,9}/[\w\-.]+"

                    # Search for the pattern in the text
                    match = re.search(doi_pattern, doi_text)

                    if match:
                        doi = match.group(0)
                    else:
                        print("DOI not found in the text.")
                        doi = ""
                except Exception as e:
                    doi = ""
                    print(f"An error occurred: {e}")

                try:
                    # pdf_link_page=article_details.find("ul",class_="value galleys_links").find("a",class_="obj_galley_link pdf").get('href')
                    pdf_link_page = article_details.find("div", class_="item galleys").find("a").get('href')
                    pdf_page=get_soup(pdf_link_page)
                    pdf_link=pdf_page.find("a",class_="download").get('href')
                except Exception as e:
                    pdf_link = ""
                    print(f"An error occurred: {e}")

                check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, "")
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count)+" article is duplicated article" +"\n"+"Article title:", Article_title,"\n")

                else:
                    print("Wait until the PDF is downloaded")
                    pdf_content = requests.get(pdf_link, headers=headers,verify=False).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")

                    data.append(
                        {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "","Volume": volume, "Issue": "", "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "","Year": year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})

                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print(get_ordinal_suffix(Article_count)+" article is original article" +"\n"+"Article title:", Article_title,"\n")

                if not pdf_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')
                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"{Article_link} : {str(error)}"
                    print(get_ordinal_suffix(Article_count)+" article could not be downloaded due to an error"+"\n"+"Article title:", Article_title,"\n")
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0
        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)),str(len(error_list)))
        except Exception as error:
            message=str(error)
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
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the site:" + str(error)
            print(Error_message, "\n")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
            url_index, url_check = url_index + 1, 0
