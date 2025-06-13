import requests
import os
import re
from datetime import datetime
import pandas as pd
import shutil
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import common_function
import tempfile

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

duplicate_list = []
error_list = []
completed_list = []
data = []
Total_count = None
attachment = None
current_date = None
current_time = None
Ref_value = None
ini_path = None
pdf_count = 1

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        pass
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')

# Function to get the driver with specified options
def get_driver(download_path):
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--version_main=108')
    prefs = {'download.default_directory': download_path}
    options.add_experimental_option('prefs', prefs)
    driver = uc.Chrome(options=options)
    errors = []
    return driver, errors

def get_driver_pdf(url, new_filename, download_path, driver, error_list):
    # Delete any existing PDF files in the download path
    for file in os.listdir(download_path):
        if file.endswith(".pdf"):
            os.remove(os.path.join(download_path, file))
    try:
        driver.get(url)
        time.sleep(5)

        while any(f.endswith('.crdownload') for f in os.listdir(download_path)):
            time.sleep(1)
        # Check if a PDF file was downloaded
        pdf_files = [f for f in os.listdir(download_path) if f.endswith(".pdf")]
        if pdf_files:
            downloaded_file = os.path.join(download_path, pdf_files[0])
            # new_file_path = os.path.join(download_path, new_filename)
            shutil.move(downloaded_file, new_filename)
            print(f"Downloaded: {new_filename}")
        else:
            error_list.append(f"PDF download failed. url: "+url)
    except Exception as e:
        error_list.append(f"PDF download failed. url: "+url)
def download_pdf(url, current_out):
    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(url)
        response.raise_for_status()
        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
        with open(output_fimeName, 'wb') as f:
            f.write(response.content)
            print(f"Downloaded: {output_fimeName}")
    except Exception as e:
        print(f"PDF download failed from {url}: {e}")
# Function to extract month and year
def extract_month_year(soup):
    month_year_text = soup.find("div", class_="page-heading").find("h1").get_text(strip=True)
    pattern = r'(?P<month>\w+)\s(?P<year>\d{4})'
    match = re.match(pattern, month_year_text)
    if match:
        month = match.group('month')
        year = match.group('year')
        return month, year
    return None, None

ref_66_download_path = os.path.join(tempfile.gettempdir(), 'ref_66_download')
if not os.path.exists(ref_66_download_path):
    os.makedirs(ref_66_download_path)
print(ref_66_download_path)

url_info_list = []
with open('urlDetails.txt', 'r') as file:
    for line in file:
        url, url_id = line.strip().split(',')
        url_info_list.append({"url": url, "url_id": url_id})

for url_info in url_info_list:
    try:
        url = url_info["url"]
        url_id = url_info["url_id"]

        driver, init_errors = get_driver(ref_66_download_path)

        if driver is None:
            print("Driver initiation failed. Errors:", init_errors)
            error_list.extend(init_errors)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list), ini_path, attachment, current_date, current_time,
                                                 Ref_value)
        else:
            print("Driver initiation success.")

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "Info.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        Ref_value = "66"

        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        current_issue_ele = soup.find("div", class_="navContainer").find("ul", class_="subnav").find_all("li")[1].find("a").get("href")
        current_issue_link = "https://ajph.aphapublications.org" + current_issue_ele

        driver.get(current_issue_link)
        time.sleep(5)
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')

        month, year = extract_month_year(soup2)
        if month and year:
            print(f"Month: {month}, Year: {year}")
        else:
            print("Could not extract month and year")

        All_articles = soup2.find_all('div', class_='articleEntry')

        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link = None
            try:
                Article_link = 'https://ajph.aphapublications.org' + All_articles[article_index].find("div", class_="art_title linkable").find('a', class_="ref nowrap").get('href')
                Article_title = All_articles[article_index].find("div", class_="art_title linkable").find('a').find("span", class_="hlFld-Title").text.strip()
                volume_issue_text = All_articles[article_index].find("span", class_="issueInfo").get_text(strip=True)
                pattern = r'(?P<volume>\d+)\((?P<issue>S?\d+)\)'
                match = re.match(pattern, volume_issue_text)
                if match:
                    volume = match.group('volume')
                    issue = match.group('issue')
                page_range_text = All_articles[article_index].find("span", class_="articlePageRange").get_text(strip=True)
                pattern = r'pp\.\s*(?P<start_page>S?\d+)[–-](?P<end_page>S?\d+)'
                page_range_match = re.search(pattern, page_range_text)

                if page_range_match:
                    start_page = page_range_match.group('start_page')
                    end_page = page_range_match.group('end_page')
                    page_range = f"{start_page}–{end_page}"
                    print(f"Page range: {page_range}")

                driver.get(Article_link)
                time.sleep(5)
                soup3 = BeautifulSoup(driver.page_source, 'html.parser')

                doi = soup3.find("ul", class_="tab-nav").find("a",doi=True).get("doi")
                pdf_link = f'https://ajph.aphapublications.org/doi/pdf/' + doi + "?download=true"
                check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article:", Article_title)
                else:
                    pdf_save = os.path.join(current_out, f"{pdf_count}.pdf")
                    get_driver_pdf(pdf_link, pdf_save, ref_66_download_path, driver, error_list)
                    print("Original Article:", Article_title)
                    try:
                        data.append({
                            "Title": Article_title,
                            "DOI": doi,
                            "Publisher Item Type": "",
                            "ItemID": "",
                            "Identifier": "",
                            "Volume": volume,
                            "Issue": issue,
                            "Supplement": "",
                            "Part": "",
                            "Special Issue": "",
                            "Page Range": page_range,
                            "Month": month,
                            "Day": "",
                            "Year": year,
                            "URL": pdf_link,
                            "SOURCE File Name": f"{pdf_count}.pdf",
                            "user_id": user_id
                        })
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_link + '\n')

                    except Exception as error:
                        message = f"Error link - {Article_link} : {str(error)}"
                        error_list.append(message)
                        print(error)
                article_index, article_check = article_index + 1, 0
            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"Error link - {Article_link} : {str(error)}"
                    print("Download failed:", Article_title)
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
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass


    except Exception as error:
        Error_message = "Error in the site: " + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

    finally:
        if driver:
            driver.close()
