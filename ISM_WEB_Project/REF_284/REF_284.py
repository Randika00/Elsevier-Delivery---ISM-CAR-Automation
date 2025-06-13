import re

import driver
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from datetime import datetime
import captcha_main
import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver
import common_function

# Install and initialize ChromeDriver
chromedriver.install()


def get_soup(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def init_driver():
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    options = uc.ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(f'--user-agent={user_agent}')
    driver = uc.Chrome(options=options)
    return driver

def use_driver(driver, url, request_cookies):

    driver.get(url)
    for cookie_name, cookie_value in request_cookies.items():
        driver.add_cookie({"name": cookie_name, "value": cookie_value})
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    return soup


request_cookies ={
    "American_Academy_of_PediatricsMachineID": "638449428831762803",
    "fpestid": "nArwBRwYpwen-bzYiCaag8sRm0A_svWW40U9_gGnzkypDnE3dLInxu3MP6Aixm8n6CcpkQ",
    "hum_aap_visitor": "051d09ad-0048-4508-a2e8-1c2b8667ad1b",
    "__gpi": "UID=00000d21489e6c28:T=1709346088:RT=1709603021:S=ALNI_MazpA53OPDPvGmjXGGgijfxpw5PWA",
    "_ga_G5TCNFJCYP": "GS1.1.1710739975.8.1.1710739980.0.0.0",
    "_cc_id": "887b3cc2fb5997a3d7d85844831d28a",
    "panoramaId_expiry": "1723694759644",
    "panoramaId": "e5eb3f00e17efcbf409186debc7316d539381fc443dfe90bded564c62381a31d",
    "panoramaIdType": "panoIndiv",
    "_gid": "GA1.2.1519307360.1723089960",
    "AAP2_SessionId": "4od3qqyw2xabienzpjileery",
    "__cf_bm": "LsdCV1kDpmKppk3LnSCzUeJiKNygmO_pl2qnWcU9Os4-1723185389-1.0.1.1-I7il6fOQzFAjF0dQVFlZy7FIqD_qskBmxFBoFJZ0sFD2YCaul.gBvV5nmJzI6WmPT26KEDBX0oNMJ8Uvtpmg4A",
    "feathr_session_id": "66b5b8efb343920046f395b8",
    "_dc_gtm_UA-53057564-11": "1",
    "__gads": "ID=27717ecb3d043fed:T=1709346088:RT=1723185391:S=ALNI_MbJ7QppOeJzIZIUyi5jKWVOY5JeYA",
    "__eoi": "ID=b346539b1b2679fb:T=1709346088:RT=1723185391:S=AA-AfjaxBD07Nk1iaDu9WbKQsKT1",
    "lotame_domain_check": "aap.org",
    "cf_clearance": "3yP0L7v_kxdduOOkKE.VJdrxFIQl9sL1A_iAkTovfSc-1723185436-1.0.1.1-.vke2jowcYmaLdDMFWnpWmephAoeJhfSRfnLl82b6.yfUpEYOGmys6g5OP387M_1tGxwFXbZAUA36O3Vs86HAQ",
    "_ga_2162JJ7E97": "GS1.1.1723185391.24.1.1723185443.0.0.0",
    "_ga_FD9D3XZVQQ": "GS1.1.1723185391.24.1.1723185443.0.0.0",
    "_ga": "GA1.2.293847094.1709346089"
}

driver = None
driver = init_driver()
# Create a session object
session = requests.Session()


def download_pdf(pdf_link, headers, current_out, pdf_count, article_count, max_retries=10):
    output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
    retry_count = 0
    success = False

    while retry_count < max_retries and not success:
        try:
            response = session.get(pdf_link, headers=headers)
            response.raise_for_status()
            pdf_content = response.content
            with open(output_fileName, 'wb') as file:
                file.write(pdf_content)
            success = True
            print(f"{get_ordinal_suffix(pdf_count)} PDF file has been successfully downloaded")
        except Exception as e:
            retry_count += 1
            print(f"Failed to download PDF on attempt {retry_count}. Error: {e}")
            if retry_count == max_retries:
                print("Maximum retry attempts reached, download failed.")

    return success


def get_ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
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
        url_list = file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\" : " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)

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
        print(f"Processing URL: {url} with ID: {url_id}")

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            ini_path = os.path.join(os.getcwd(), "REF_284.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "284"
        print(url_id)

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1
        article_count = 1

        soup = get_soup(url, headers)
        if soup.find("div", class_='explanation-message') is not None:
            try:
                print("Attempting to solve CAPTCHA 1 using UC.")
                if not driver:
                    driver = init_driver()
                soup = use_driver(driver, url, request_cookies)
                print("Solved the CAPTCHA 1 Using UC.")

            except Exception as e:
                print(f"Attempting to solve CAPTCHA 1 using fallback method. Error: {e}")
                response = captcha_main.captcha_main(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                print("Solved the CAPTCHA 1.")

        vol_iss_text = soup.find("span", class_="volume issue").get_text(strip=True)
        match = re.search(r"Volume (\d+)(?:, Issue ([\d\-]+))?", vol_iss_text)
        if match:
            volume = match.group(1) if match.group(1) is not None else ""
            issue = match.group(2) if match.group(2) is not None else ""
            print(f"Volume: {volume}, Issue: {issue}")
        else:
            print("No match found")

        year_month_text = soup.find("div", class_="ii-pub-date").get_text(strip=True)
        match = re.search(r"([A-Za-z]+) (\d{4})", year_month_text)
        if match:
            month = match.group(1)
            year = match.group(2)
            print(f"Month: {month}, Year: {year}")
        else:
            print("No match found")

        All_articles = soup.findAll("div", class_="al-article-items")

        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index + 1
            Article_link, Article_title = None, None
            try:
                Article_title = All_articles[article_index].find("h5", class_="customLink item-title").find("a").text.strip()
                Article_link = "https://publications.aap.org" + All_articles[article_index].find("h5",class_="customLink item-title").find("a").get("href")
                try:
                    soup2 = get_soup(Article_link, headers)
                    Article_title = soup2.find('h1', class_="wi-article-title article-title-main").text.strip()
                except Exception as e:
                    try:
                        print(f"Attempting to solve CAPTCHA 2 using UC for {Article_link}. Error: {e}")
                        soup2 = use_driver(driver, Article_link, request_cookies)
                        Article_title = soup2.find('h1', class_="wi-article-title article-title-main").text.strip()
                        print("Solved the CAPTCHA 2 Using UC.")

                    except Exception as e:
                        print(f"Attempting to solve CAPTCHA 2 using fallback method for {Article_link}. Error: {e}")
                        response1 = captcha_main.captcha_main(Article_link)
                        soup2 = BeautifulSoup(response1.content, 'html.parser')
                        Article_title = soup2.find('h1', class_="wi-article-title article-title-main").text.strip()
                        print("Solved the CAPTCHA 2.")

                page_range_text = soup2.find("div", class_="ww-citation-primary").get_text(strip=True)
                match = re.search(r": (\w*\d+[\–\-]\w*\d+)", page_range_text)
                if match:
                    page_range = match.group(1)
                    print(f"Page Range: {page_range}")
                else:
                    page_range = ""
                    print(f"Page Range: {page_range}")

                try:
                    DOI = soup2.find("div", class_="citation-doi").find("a").text.strip().rsplit("org/", 1)[-1]
                except:
                    print("Failed to find DOI")
                    DOI = ""

                pdf_link = "https://publications.aap.org" + soup2.find('a',class_="al-link pdf openInAnotherWindow stats-item-pdf-download js-download-file-gtm-datalayer-event article-pdfLink").get('href')

                if article_check == 0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, volume, issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID: {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count) + " article is duplicated article\n" + "Article title:",
                          Article_title, "\n")
                else:
                    print("Wait until the PDF is downloaded")
                    success = download_pdf(pdf_link, headers, current_out, pdf_count, article_count)
                    if success:
                        data.append({
                            "Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                            "Identifier": "", "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                            "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "",
                            "Year": year, "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                            "user_id": user_id
                        })

                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print(get_ordinal_suffix(Article_count) + " article is original article\n" + "Article title:",
                              Article_title, "\n")

                if Article_link not in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0
            except Exception as error:
                if article_check < 0:
                    article_check += 1
                else:
                    message = f"{Article_link} : {str(error)}"
                    print(get_ordinal_suffix(Article_count) + " article could not be downloaded due to an error\n" + "Article title:",Article_title, "\n")
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
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the site: " + str(error)
            print(Error_message, "\n")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)

            url_index, url_check = url_index + 1, 0

if driver:
    driver.close()
    driver.quit()
