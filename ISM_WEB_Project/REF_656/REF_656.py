import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd



def print_bordered_message(message):
    border_length = len(message) + 4
    border = "-" * (border_length - 2)

    print(f"+{border}+")
    print(f"| {message} |")
    print(f"+{border}+")
    print()

def get_soup(url,headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

session = requests.session()

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
        print(url_id)
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        Ref_value = "656"

        ini_path = os.path.join(os.getcwd(), "REF_656.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1

        session = requests.session()

        headers1 = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "connection": "keep-alive",
            # "cookie": "OJSSID=g65evbj7m26n497emscd5c02c5",
            "host": "www.eemj.eu",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

        session.get(url, headers=headers1)

        login_link = 'https://www.eemj.eu/index.php/EEMJ/login/signIn'

        headers2 = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "content-length": "46",
            "content-type": "application/x-www-form-urlencoded",
            # "cookie": "OJSSID=g65evbj7m26n497emscd5c02c5",
            "origin": "https://www.eemj.eu",
            "priority": "u=0, i",
            "referer": "https://www.eemj.eu/index.php/EEMJ/login/signIn",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

        pay_load = {"source:": "",
                    "username": "full_access",
                    "password": "13243546"}

        session.post(login_link, headers=headers2, data=pay_load)

        user_link = 'https://www.eemj.eu/index.php/EEMJ/user'

        headers3 = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            # "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            # "cookie": "OJSSID=u0njn2p4cqrgrubhibmbea9on3",
            "priority": "u=0, i",
            "referer": "https://www.eemj.eu/index.php/EEMJ/login/signIn",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

        res2 = session.get(user_link, headers=headers3)

        headers4 = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            # "cookie": "OJSSID=u0njn2p4cqrgrubhibmbea9on3",
            "priority": "u=0, i",
            "referer": "https://www.eemj.eu/index.php/EEMJ/issue/view/264",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

        headers5 = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            # "cookie": "OJSSID=u0njn2p4cqrgrubhibmbea9on3",
            "priority": "u=0, i",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

        soup = BeautifulSoup(res2.content, "html.parser")
        current_link = soup.find("li", id="current").find("a").get('href')
        soup2 = get_soup(current_link, headers=headers1)
        # res3 = session.get(current_link, headers=headers)
        # soup2 = BeautifulSoup(res3.content, "html.parser")
        year_text = soup2.find("h2").get_text(strip=True)
        pattern = r"Vol\s(\d+),\sNo\s(\d+)\s\((\d{4})\)"
        match = re.search(pattern, year_text)
        if match:
            volume = match.group(1)
            issue = match.group(2)
            year = match.group(3)
            print(f"Volume: {volume}, Issue: {issue}, Year: {year}")
        else:
            print("No match found")

        articles = soup2.find_all("table", class_="tocArticle")
        Total_count = len(articles)
        print(f"Total number of articles: {Total_count}\n")
        for article in articles:
            Article_link = None
            try:
                Article_link = article.find("div", class_="tocTitle").find('a').get('href')
                page_range = article.find("div", class_="tocPages").get_text(strip=True)
                article_response = session.get(Article_link, headers=headers4)
                soup4 = BeautifulSoup(article_response.content, 'html.parser')
                Article_title = soup4.find("h3").get_text(strip=True)
                pdf_link = soup4.find("div", attrs={"id": "articleFullText"}).a["href"].replace("view", "download")
                print(pdf_link)

                check_value, tpa_id = common_function.check_duplicate("", Article_title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)

                else:
                    pdf_content = session.get(pdf_link, headers=headers5).content
                    output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fileName, 'wb') as file:
                        file.write(pdf_content)
                    print(f"Downloaded: {output_fileName}")
                    data.append(
                        {"Title": Article_title, "DOI": "", "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range":page_range, "Month": "", "Day": "",
                         "Year": year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title)

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')
            except Exception as error:
                message = f"Error link - {Article_link} : {str(error)}"
                print("Download failed :", Article_title)
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
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 0:
            url_check += 1
        else:
            Error_message = "Error in the site:" + str(error)
            print_bordered_message(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)
            url_index, url_check = url_index + 1, 0
    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)