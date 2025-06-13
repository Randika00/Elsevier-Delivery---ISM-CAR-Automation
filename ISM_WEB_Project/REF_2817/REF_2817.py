import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, time
import common_function
import pandas as pd
import PyPDF2
import io



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}


def extract_article_info(text_list):
    # Initialize variables
    Article_title = []
    page_range = None

    for line in text_list:
        line = line.strip()  # Clean up whitespace

        # Check if the line contains "Pages:"
        if line.startswith("Pages:"):
            # Extract the page range
            page_range = line.replace("Pages:", "").strip()
        else:
            # Append to the article title list
            Article_title.append(line)

    # Join the article title parts into a single string, excluding author names
    Article_title = " ".join(Article_title[1:]).strip()  # Ignoring the first line which is author names

    return Article_title, page_range
def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Check for meta refresh tag
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if meta_refresh:
        wait, new_url = meta_refresh['content'].split(';')
        if new_url.lower().strip().startswith("url="):
            new_url = new_url[4:].strip()
            # Follow the redirect URL
            return get_soup(new_url)
    return soup

def get_soup_with_session(url):
    session = requests.Session()
    session.headers = {'User-Agent': 'Mozilla/5.0'}
    response = session.get(url)
    return BeautifulSoup(response.content, 'html.parser')
def get_token(url):
    response = requests.get(url,headers=headers)
    cookie=response.cookies
    print(cookie)
    token=cookie.get("wkxt3_csrf_token").replace("-","")
    return token

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
            ini_path = os.path.join(os.getcwd(), "REF_2817.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "2817"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1
        url_value = url.split('/')[-3]

        soup = get_soup(url)

        current_issue_href="https://smr.krasgmu.ru/"+soup.find("div",class_="page").find('a',class_="thisblock").get('href')
        current_issue_link_soup=get_soup(current_issue_href)
        current_issue_link="https://smr.krasgmu.ru/"+current_issue_link_soup.find_all("a",class_="thisblock")[-1].get('href')
        current_issue_soup = get_soup(current_issue_link)

        EN_href="https://smr.krasgmu.ru/"+current_issue_soup.find('li',id="flag").find('a',class_="mm").get('href')
        EN_soup=get_soup(EN_href)

        combine_soup=str(current_issue_soup)+str(EN_soup)
        TOC_path, TOC_name = common_function.output_TOC_name(current_out)
        with open(TOC_path, 'w', encoding='utf-8') as html_file:
            html_file.write(str(combine_soup))

        vol_issue_text=EN_soup.find("div",class_="divcirclephototext").get_text(strip=True)
        pattern = r"(?P<year>\d{4})\.\s*№\s*(?P<issue>\d+)"

        # Extracting using regex
        match = re.search(pattern, vol_issue_text)

        if match:
            year = match.group('year')
            issue = match.group('issue')

            print(f"Year: {year}, Issue: {issue}")
        else:
            print("No match found")

        All_articles = EN_soup.find_all("div",class_="papertitle")
        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}", "\n")

        paired_divs = []
        for title in All_articles:
            next_div = title.find_next_sibling('div')
            if next_div:
                paired_divs.append(f'{str(title)}{str(next_div)}')
        article_index, article_check = 0, 0
        while article_index < len(paired_divs):
            Article_count = article_index + 1
            Article_title = None
            try:
                soup2 = BeautifulSoup(paired_divs[article_index], 'html.parser')
                a_tag = soup2.find('a').contents

                if str(a_tag[1]) != '<br/>':
                    Article_title = re.search(r"(?<=<br>)([^<]+)(?=<br/?>)", str(a_tag[1])).group(1)
                else:
                    Article_title = a_tag[2].get_text(strip=True) if len(a_tag) > 2 else ""

                print(Article_title)
                text = soup2.find("a").get_text(strip=True)
                match = re.search(r'Pages:\s*(\d+-\d+)', text)

                if match:
                    page_range = match.group(1)
                    print(f"Page Range: {page_range}")
                else:
                    print("Could not find page range in the text.")

                pdf_link = soup2.find('a',class_="flr").get("href")

                doi_pattern = r"DOI\s*([\d\.\/\-]+)"
                souptext=soup2.text
                doi_match = re.search(doi_pattern, souptext)

                if doi_match:
                    doi = doi_match.group(1)
                    print(f"Extracted DOI: {doi}")
                else:
                    print("DOI not found.")
                print_bordered_message(f"page_range: {page_range},pdf_link:{pdf_link}")

                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate("", Article_title, url_id, "", issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{pdf_link} - duplicate record with TPAID : {tpa_id}"
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
                             "Volume": "", "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                             "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{pdf_link} - Scraped"
                        completed_list.append(scrape_message)
                        print(get_ordinal_suffix(Article_count)+" article is original article" +"\n"+"Article title:", Article_title,"✅"+ '\n')

                article_index, article_check = article_index + 1, 0
            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"Error link - {pdf_link} : {str(error)}"
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

    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)
