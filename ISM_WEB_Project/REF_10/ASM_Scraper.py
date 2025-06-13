from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from datetime import datetime
import shutil
import common_function
import chromedriver_autoinstaller as chromedriver
chromedriver.install()

Total_count=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
titles = []
data = []
vol=[]
iss=[]
months=[]
years=[]
error_list=[]
pdf_count =1
try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://journals.asm.org/loi/spectrum',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    "Content-Type": "text/html;charset=UTF-8",
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
def download_pdf(url, current_out):
    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(url,timeout=10000)
        response.raise_for_status()
        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
        with open(output_fimeName, 'wb') as f:
            f.write(response.content)
            print(f"Downloaded: {output_fimeName}")
    except Exception as e:
        print(f"PDF download failed from {url}: {e}")
        error_message = f"download pdf Failed: {e}"
        error_list.append(error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)


def initialize_driver_with_retry():
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            return uc.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        except WebDriverException as e:
            print(f"Failed to initialize WebDriver. Retrying... ({retries+1}/{max_retries})")
            error_message = f"Attempt {retries} - WebDriver initialization failed: {e}"
            retries += 1
            error_list.append(error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)
    print("Failed to initialize WebDriver after multiple retries. Exiting.")
    return None
def create_custom_wait(driver, timeout=30, poll_frequency=0.5, ignored_exceptions=None):
    if ignored_exceptions is None:
        ignored_exceptions = [NoSuchElementException, TimeoutException]
    return WebDriverWait(driver, timeout, poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)

def scrape_journal_data(page_url, count):
    global pdf_count,current_out,Total_count
    soup = BeautifulSoup(page_url.page_source, "html.parser")
    current_links = soup.find('div', class_='table-of-content').find_all('div', class_='issue-item')
    Total_count = len(current_links)
    print(f"Total number of articles:{Total_count}", "\n")
    for i, current_link in enumerate(current_links):
        Article_link = None
        try:
            a_element1 = current_link.find('a')
            Article_link="https://journals.asm.org"+a_element1.get("href")
            title = current_link.find('div', class_='issue-item__title').find('h3').get_text(strip=True)
            DOI = current_link.find('div', class_='issue-item__doi').find('a').getText(strip=True)[16:]
            if count == 1:
                metadata = soup.find('h2', class_='toc__title')
                if metadata:
                    span_content = metadata.find('span').text
                    parts = span_content.split('•')
                    Volume = parts[0].strip().split()[1]
                    Issue = parts[1].strip().split()[1]
                    month = parts[2].strip().split()[0]
                    year = parts[2].strip().split()[1]
                vol.append(Volume)
                iss.append(Issue)
                months.append(month)
                years.append(year)
            elif count==0:
                Volume = vol[0]
                Issue = iss[0]
                month=months[0]
                year=years[0]
            encode_Journal_link = 'https://journals.asm.org' + a_element1.get("href") + '?download=true'
            insertion_point = encode_Journal_link.find('/doi') + 4
            modified_url = encode_Journal_link[:insertion_point] + '/pdf' + encode_Journal_link[insertion_point:]
            check_value,tpa_id = common_function.check_duplicate(DOI, title, url_id, Volume, Issue)
            if Check_duplicate.lower()=="true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", title)
            else:
                print("Original Article :", title)
                download_pdf(modified_url, current_out)
                data.append({"Title": title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": "", "Month": month, "Day": "", "Year": year,
                             "URL": modified_url, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                pdf_count += 1
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
            if not modified_url in read_content:
                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                    write_file.write(Article_link + '\n')

        except Exception as current_links_error:
            print(f"An error occurred while downloading the PDF: {current_links_error}")
            message = f"Error link - {Article_link} : {str(current_links_error)}"
            error_list.append(message)
    return data


# # Create an instance of Options
# chrome_options = Options()
# # chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--incognito")

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

chrome_options = uc.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument(f'--user-agent={user_agent}')

try:
    driver = initialize_driver_with_retry()
    driver.set_window_size(1000, 750)
    driver.set_page_load_timeout(600)
    fluent_wait = create_custom_wait(driver, timeout=10, poll_frequency=0.5)

    url_info_list = []
    with open('ASM_links.txt', 'r') as file:
        for line in file:
            url, url_id = line.strip().split(',')
            url_info_list.append({"url": url, "url_id": url_id})


    for url_info in url_info_list:
        try:
            attachment = None
            url = url_info["url"]
            url_id = url_info["url_id"]
            pdf_count = 1

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "ASM.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            Ref_value = "10"

            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)
            print(url_id)

            driver.get(url)
            wait = WebDriverWait(driver, 10)
            if "/journal/" in url:
                element_xpath = "//div[@class='current-issue__actions']/a[contains(text(), 'View Current Issue')]"
            else:
                element_xpath = "//li//div[@class='status current' and text()='CURRENT ISSUE']"

            element = fluent_wait.until(lambda d: d.find_element(By.XPATH, element_xpath))
            driver.execute_script("arguments[0].click();", element)
            scrape_journal_data(driver, 1)

            Next_page = fluent_wait.until(lambda d: d.find_element(By.XPATH,"//a[contains(@class, 'content-navigation__btn--next') and .//span[text()='Next Issue']]"))
            driver.execute_script("arguments[0].click();", Next_page)
            scrape_journal_data(driver, 0)

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

        except Exception as url_info_error:
            print(f"An error occurred for URL ID {url_id}: {url_info_error}")
            message = f"Error id - {url_id} : {str(url_info_error)}"
            error_list.append(message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)
        finally:
            subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
            error_file_path = os.path.join(current_out, 'download_details.html')
            with open(error_file_path, 'w', encoding='utf-8') as file:
                file.write(error_html_content)
            print("Error details file saved to:", error_file_path)
    driver.quit()

except WebDriverException as e:
    print(f"Failed to initialize WebDriver: {e}")
    message = f"Error id - {url_id} : {str(e)}"
    error_list.append(message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

