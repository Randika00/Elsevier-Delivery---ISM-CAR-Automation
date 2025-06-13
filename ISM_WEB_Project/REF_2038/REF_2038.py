import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, time
import common_function
import pandas as pd
import io
import pdfplumber

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

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
            ini_path = os.path.join(os.getcwd(), "REF_2038.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "2038"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1
        url_value = url.split('/')[-3]

        en_soup = get_soup(url)

        CN_href="https://actaps.sinh.ac.cn/"+en_soup.find('ul',class_="nav navbar-nav").find_all('a')[-1].get('href')
        CN_soup=get_soup(CN_href)

        combine_soup=str(en_soup)+str(CN_soup)
        TOC_path, TOC_name = common_function.output_TOC_name(current_out)
        with open(TOC_path, 'w', encoding='utf-8') as html_file:
            html_file.write(str(combine_soup))

        vol_issue_text=en_soup.find("p",class_="bt_ju").get_text(strip=True)
        vol_issue_match = re.search(r"(\d{4})年，Vol\. (\d+)", vol_issue_text)

        if vol_issue_match:
            year = vol_issue_match.group(1)
            volume = vol_issue_match.group(2)
        else:
            print("No match found")
        divs = en_soup.find_all('div', class_="col-lg-2 col-md-2 col-sm-4 col-xs-4 text-center")
        divs_with_a_tag = [div for div in divs if div.find('a', href=True)]
        last_div_with_a_tag = divs_with_a_tag[-1] if divs_with_a_tag else None
        text=last_div_with_a_tag.get_text(strip=True)
        month_map = {
            "Jan.": "January", "Feb.": "February", "Mar.": "March",
            "Apr.": "April", "May": "May", "Jun.": "June",
            "Jul.": "July", "Aug.": "August", "Sep.": "September",
            "Oct.": "October", "Nov.": "November", "Dec.": "December"
        }
        match = re.search(r"([A-Za-z]+)\. (\d+), No\. (\d+)", text)

        if match:
            month_abbr = match.group(1) + "."
            date = match.group(2)
            issue = match.group(3)

            # Convert abbreviated month to full month name
            full_month = month_map.get(month_abbr, "Unknown month")

            print(f"Year: {year},Month: {full_month}, Date: {date}, Volume: {volume}, Issue: {issue}")
        else:
            print("No match found")

        current_issue_link="https://actaps.sinh.ac.cn/"+last_div_with_a_tag.find('a').get('href')
        current_issue_soup=get_soup(current_issue_link)

        All_articles = current_issue_soup.find("div",class_="col-lg-9 col-md-9 col-sm-8 col-xs-8").find_all("li")
        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}", "\n")
        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index + 1
            Article_link, Article_title = None, None
            try:
                Article_link = "https://actaps.sinh.ac.cn/"+All_articles[article_index].find("a").get('href')

                pdf_page_soup=get_soup(Article_link)

                Article_title = pdf_page_soup.find("p",class_="in_abst").get_text(strip=True)
                meta_data=pdf_page_soup.find("div", class_="info text-right").get_text(strip=True)
                match = re.search(r": (\d+-\d+)", meta_data)

                if match:
                    page_range = match.group(1)
                else:
                    print("No page range found")

                pdf_link = "https://actaps.sinh.ac.cn/"+pdf_page_soup.find('div',class_="panel-body").find_all("li")[1].find('a').get("href")
                print_bordered_message(f"page_range: {page_range},pdf_link:{pdf_link}")

                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate("", Article_title, url_id, volume, issue)
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
                        try:
                            response = session.get(pdf_link, headers=headers)
                            if 'html' in response.headers.get('Content-Type', ''):
                                redirect_url_match = re.search(r"location.replace\('(.+?)'\)", response.text)
                                if redirect_url_match:
                                    redirect_url = redirect_url_match.group(1)
                                    if not redirect_url.startswith('http'):
                                        base_url = pdf_link.rsplit('/', 1)[0]
                                        pdf_link = base_url + '/' + redirect_url
                                    response = session.get(pdf_link, headers=headers)
                            pdf_content = response.content
                            output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")

                            with open(output_fileName, 'wb') as file:
                                file.write(pdf_content)

                            if os.path.getsize(output_fileName) > 0:
                                print(f"Downloaded: {output_fileName}")
                                download_successful = True
                            else:
                                raise ValueError("Downloaded file is empty")

                        except Exception as e:
                            retries += 1
                            print(f"Retrying download... Attempt {retries}/{max_retries}. Error: {e}")
                            time.sleep(5)

                    if download_successful:
                        data.append(
                            {"Title": Article_title, "DOI": "", "Publisher Item Type": "", "ItemID": "",
                             "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": full_month, "Day": date, "Year": year,
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

    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)
