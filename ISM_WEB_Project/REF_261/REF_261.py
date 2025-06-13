import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd

def get_soup(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

session = requests.session()

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
try:
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")
    url_id="915473815"
    Ref_value = "261"

    ini_path = os.path.join(os.getcwd(), "REF_261.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    Article_link = 'https://history.jes.su/index.php?dispatch=issues.archive&sl=en'
    url = "https://history.jes.su/"

    mainheaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'history.jes.su',
    'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    first_page = session.get(Article_link, headers=mainheaders)
    id = BeautifulSoup(first_page.content, 'html.parser').find('input', {'name': 'security_hash'}).get('value')
    pay_load = {"return_url": "index.php?dispatch = issues.archive & sl = en",
                "redirect_url": "index.php?dispatch = issues.archive & sl = en",
                "user_login": "guest@jes.su",
                "password": "support1234",
                "dispatch[auth.login]":"",
                "security_hash": id}

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'history.jes.su',
        'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    login_response = session.post(url, headers=headers, data=pay_load)

    cookies_main = login_response.cookies
    cookie_str = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookies_main])

    headers_main ={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': cookie_str,
        'Host': 'history.jes.su',
        'Referer': 'https://history.jes.su/index.php?dispatch=issues.archive&sl=en',
        'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    res2 = session.get('https://history.jes.su/index.php?dispatch=issues.archive&sl=en', headers=headers_main)
    soup2 = BeautifulSoup(res2.content, "html.parser")
    year=soup2.find("span",class_="issues-years-one-top-title").get_text(strip=True)
    archive_url=soup2.find("div",class_="issues").find("div","issues-one clearfix").find("a").get('href')
    archive_page = session.get(archive_url, headers=headers)
    archive_page.raise_for_status()
    soup3 = BeautifulSoup(archive_page.content, 'html.parser')

    CN_href = soup3.find_all('li', class_="ty-select-block__list-item")[1].find('a').get('href')
    CN_soup = get_soup(CN_href)

    combine_soup = str(soup3) + str(CN_soup)
    TOC_path, TOC_name = common_function.output_TOC_name(current_out)
    with open(TOC_path, 'w', encoding='utf-8') as html_file:
        html_file.write(str(combine_soup))

    articles=soup3.find_all("div",class_="issue-articles-one subscribe clearfix")
    Total_count = len(articles)
    print(f"Total number of articles: {Total_count}\n")
    for article in articles:
        Article_link = None
        try:
            Article_link = article.find('a').get('href')
            article_response=session.get(Article_link, headers=headers)
            soup4 = BeautifulSoup(article_response.content, 'html.parser')
            Article_title=soup4.find("div",class_="pub-title").get_text(strip=True)
            doi=soup4.find_all("div",class_="pub-annotation-info-one-value")[1].find("a").get_text(strip=True)
            vol_text=soup4.find_all("div",class_="pub-annotation-info-one-value")[5].find("a").get_text(strip=True)
            pattern = r"Volume (\d+) Issue (\d+)"
            match = re.search(pattern, vol_text)
            if match:
                volume = match.group(1)
                issue = match.group(2)
            else:
                print("No match found")
            pdf_link=soup4.find("a",class_="ty-btn ty-btn__tertiary").get('href')

            check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
            if Check_duplicate.lower() == "true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", Article_title)

            else:
                pdf_content = session.get(pdf_link, headers=headers).content
                output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                with open(output_fileName, 'wb') as file:
                    file.write(pdf_content)
                print(f"Downloaded: {output_fileName}")
                data.append(
                    {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                     "Identifier": "",
                     "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                     "Special Issue": "", "Page Range": "", "Month": "", "Day": "",
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
    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass
except Exception as error:
    Error_message = "Error in the site:" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
finally:
    subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
    error_file_path = os.path.join(current_out, 'download_details.html')
    with open(error_file_path, 'w', encoding='utf-8') as file:
        file.write(error_html_content)
    print("Error details file saved to:", error_file_path)