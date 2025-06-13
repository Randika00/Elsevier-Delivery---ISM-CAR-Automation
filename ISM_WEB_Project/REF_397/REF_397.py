import re
import requests
import cloudscraper
from bs4 import BeautifulSoup
import os
import common_function
import pandas as pd
from datetime import datetime
import random

scraper = cloudscraper.create_scraper()

def get_soup(url):
    response = scraper.get(url)
    soup= BeautifulSoup(response.content, 'html.parser')
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


def get_token(url):
    response = requests.get(url, headers=headers)
    cookie = response.cookies
    token = cookie.get("wkxt3_csrf_token").replace("-", "")
    return token


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

headers2 = {
    ':authority': 'medscimonit.com',
    ':method': 'POST',
    ':path': '/download/getFreePdf/l/EN',
    ':scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'content-length': '23',  # Adjust as per payload
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': '_ga=GA1.1.1217681088.1727054354; PHPSESSID=c499jg2jr18j9j185lpjid3i1s; cf_clearance=Z5EDegFibehupzz0qsT105C3iULNaiM5nJOwB7dBx8g-1727156453-1.2.1.1-TmExNJH_tEf4GJJ9pEqvnwuG8hS469kzIcah_R0506IF.h3yap9UOni.l1EYgLqqY2o26TD.TJknys.hdCSjXue4mxOq0My_skziUVb6XBaTyFvJiO7CN5GM6zuQDy_LtAk_rFzNIyPc5q8pVtUSVesLSgrToapjJTln3lE9WkbvX49sx3dNxpc2rs0S6_6auUkaJyhcj74ecOy7aSUqCW15SHiFwz5lnaLNmjtdY9j55hxk7QS5j54XDemJTL9v1hIisyTk.cGS13f.dZYenJR4LvLLJxYbfyaxZE_AFztGPo9F0p9Gj6tK7k4sg3Df4.vWlr8Dz9B6smJrwtaBTzTyJo9pgNvo3cbuMq86QkO_OmJlvvFrXeJ4XH3KAAGnPx24SuzGZwK900HrOy.pSQ; _ga_3SRH1HZX4T=GS1.1.1727156450.3.1.1727156511.59.0.0',  # Insert the exact cookies
    'origin': 'https://medscimonit.com',
    'priority': 'u=0, i',
    'referer': 'https://medscimonit.com/abstract/index/idArt/945450',  # Update with actual referer
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
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
            ini_path = os.path.join(os.getcwd(), "REF_397.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "397"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        attachment = None
        pdf_count = 1

        soup=get_soup(url)

        total_pages = 13
        for page_num in range(1, total_pages + 1):
            try:
                current_issue = f"https://medscimonit.com/index/currentissue/pg/{page_num}"
                print(f"Scraping page {page_num}: {current_issue}")
                current_issue_soup=get_soup(current_issue)
                date_time_meta=current_issue_soup.find("h1",class_="h4 color-blue mt-0 mb-4 pl-1").get_text(strip=True)
                match = re.search(r"Volume (\d+), (\d{4})", date_time_meta)

                if match:
                    volume = match.group(1)
                    year = match.group(2)
                    print(f"Volume: {volume}, Year: {year}")
                else:
                    print("No match found")
                All_articles =current_issue_soup.find_all("div",class_="col-10")
                Total_count = len(All_articles)
                print(f"Total number of articles: {Total_count}\n")

                article_index, article_check = 0, 0
                while article_index < len(All_articles):
                    Article_count = article_index + 1
                    Article_link, Article_title = None, None
                    try:
                        Article_link = All_articles[article_index].find("h3", class_="mt-0 mb-2 h6").find("a",class_="color-secondary mb-1 no-hover text-break").get("href")
                        Article_title = All_articles[article_index].find("h3", class_="mt-0 mb-2 h6").find("a",class_="color-secondary mb-1 no-hover text-break").get_text(strip=True)
                        DOI_element = All_articles[article_index].find("p", class_="color-gray-darker mb-0 fs-08").get_text(strip=True)

                        match = re.search(r"DOI:\s*(10\.\d{4,9}/[\w.]+)\.(\d+)", DOI_element)

                        if match:
                            doi = match.group(1) + '.' + match.group(2)
                            identifier = 'e' + match.group(2)
                        else:
                            print("No match found")
                        pdf_page_soup=get_soup(Article_link)
                        pdf_form=pdf_page_soup.find("form",class_="w-100")
                        id_jour = pdf_form.find('input', {'name': 'ID_JOUR'})['value']
                        id_art = pdf_form.find('input', {'name': 'idArt'})['value']

                        print(f'ID_JOUR: {id_jour}, idArt: {id_art}')
                        pdf_link = f"https://medscimonit.com{pdf_form.get('action')}"
                        payload = {
                            'ID_JOUR': id_jour,
                            'idArt': id_art
                        }

                        print_bordered_message(f"DOI: {doi}, Identifier: {identifier},DOI: {doi},pdf_link:{pdf_link}")

                        if article_check == 0:
                            print(get_ordinal_suffix(Article_count) + " article details have been scraped")

                        check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, "")
                        if Check_duplicate.lower() == "true" and check_value:
                            message = f"{Article_link} - duplicate record with TPAID: {tpa_id}"
                            duplicate_list.append(message)
                            print(get_ordinal_suffix(Article_count) + " article is a duplicate\nArticle title: " + Article_title + "📚\n")

                        else:
                            print("Wait until the PDF is downloaded")
                            session = cloudscraper.create_scraper()
                            retries = 0
                            max_retries = 5
                            download_successful = False

                            while retries < max_retries and not download_successful:
                                try:
                                    response = session.post(pdf_link, data=payload, headers=headers)

                                    if response.status_code == 200:
                                        pdf_content = response.content
                                        output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")

                                        with open(output_fileName, 'wb') as file:
                                            file.write(pdf_content)

                                        if os.path.getsize(output_fileName) > 0:
                                            print(f"Downloaded: {output_fileName}")
                                            print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")
                                            download_successful = True
                                        else:
                                            retries += 1
                                            print(f"Retrying download... Attempt {retries}/{max_retries}")
                                    else:
                                        print(f"Failed to download. Status code: {response.status_code}")
                                        retries += 1
                                except Exception as e:
                                    print(f"Error occurred: {e}")
                                    retries += 1


                            if download_successful:
                                data.append({
                                    "Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                    "Identifier": identifier, "Volume": volume, "Issue": "", "Supplement": "", "Part": "",
                                    "Special Issue": "", "Page Range": "", "Month": "", "Day": "",
                                    "Year": year, "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                    "user_id": user_id
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

            except Exception as page_error:
                print(f"Error while scraping page {page_num}: {page_error}")
                error_list.append(f"Error on page {page_num}: {str(page_error)}")
                continue

            print("Scraping completed!")




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
