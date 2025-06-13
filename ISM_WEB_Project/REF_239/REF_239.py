import re
import time
import shutil
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller as chromedriver
from selenium.webdriver.chrome.options import Options

# Install ChromeDriver
chromedriver.install()

# Create a WebDriver instance with options
options = Options()
options.add_argument('--headless')
options.add_argument('--incognito')
options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--allow-running-insecure-content")
# options.add_argument("--ignore-certificate-errors")
# options.add_argument("--disable-web-security")

# Define directories
download_dir = r"D:\Innodata\ISM-Car_project\pythonProject\REF_239\downloads"

# Configure WebDriver to use the download directory
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)

# Initialize the driver
driver = webdriver.Chrome(options=options)

def get_soup(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# Headers for requests
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "www.dwjs.com.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

# Initialize lists and variables
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
Total_count=None
duplicate_list = []
error_list = []
completed_list = []

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

try:
    with open('urlDetails.txt','r',encoding='utf-8') as file:
        url_list=file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\" : " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)


url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        url, url_id = url_list[url_index].split(',')
        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        Ref_value = "239"

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "REF_239.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)

        driver.get(url)
        time.sleep(10)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        english_content_url = soup.find("ul", class_="nav navbar-nav").find_all("li")[23].find("a").get("href")

        driver.get(english_content_url)
        time.sleep(15)
        html_content2 = driver.page_source
        soup2 = BeautifulSoup(html_content2, 'html.parser')
        header_text = soup2.find("div", class_="n-j-q").get_text(strip=True)

        pattern = r"(\d{2}) (\w+) (\d{4}), Volume (\d+) Issue (\d+)"
        match = re.match(pattern, header_text)
        if match:
            date, month, year, volume, issue = match.groups()
        else:
            print("The input string does not match the expected format.")

        All_articles = soup2.findAll("div", class_="article-l article-w")
        Total_count = len(All_articles)
        print(f"Total number of articles:{Total_count}", "\n")
        pdf_count = 1
        for article in All_articles:
            Article_link = None
            try:
                Article_link = article.find('div', class_="j-title-1").find('a').get('href')
                Article_title = article.find('div', class_="j-title-1").find('a').text.strip()
                doi_text = article.find('div', class_="j-volumn-doi").find('a', class_="j-doi").text.strip()

                doi_pattern = r"https://doi.org/(10\.\d{4,9}/[-._;()/:A-Z0-9]+)"
                doi_match = re.search(doi_pattern, doi_text, re.IGNORECASE)
                doi = doi_match.group(1) if doi_match else "No DOI found"

                page_range_text = article.find('span', class_="j-volumn").text.strip()
                page_range_pattern = r"\d{4}, \d+\(\d+\): (\d+-\d+)\."
                page_range_match = re.search(page_range_pattern, page_range_text)
                page_range = page_range_match.group(1) if page_range_match else "No page range found"

                driver.get(Article_link)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "main_content_center_right_pdf"))
                )

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(15)

                html_content3 = driver.page_source
                soup3 = BeautifulSoup(html_content3, 'html.parser')

                check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)

                else:
                    pdf_divs = soup3.find_all("div", class_="main_content_center_right_pdf")
                    if len(pdf_divs) >= 2:
                        pdf_div = pdf_divs[1]
                        pdf_icon = pdf_div.find("i", class_="glyphicon glyphicon-save main_content_center_right_pdf_i")
                        if pdf_icon:
                            pdf_download_button_xpath = '//div[@class="main_content_center_right_pdf"]/i[@class="glyphicon glyphicon-save main_content_center_right_pdf_i"]'
                            pdf_download_button = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, pdf_download_button_xpath))
                            )
                            # Scroll to the element
                            driver.execute_script("arguments[0].scrollIntoView(true);", pdf_download_button)
                            time.sleep(1)  # Give it a moment to ensure it's scrolled into view
                            try:
                                pdf_download_button.click()
                                print("PDF download link clicked successfully.")
                            except Exception as click_error:
                                print(f"Error clicking PDF download button: {click_error}")
                                error_list.append(f"Error clicking PDF download button: {click_error}")
                        else:
                            print("PDF download icon not found.")
                            error_list.append("PDF download icon not found.")
                    else:
                        print("PDF div not found.")
                        error_list.append("PDF div not found.")
                    time.sleep(30)

                    # Move the downloaded PDF from temp directory to the target directory
                    temp_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
                    if temp_files:
                        temp_pdf_path = os.path.join(download_dir, temp_files[0])
                        pdf_save = os.path.join(current_out, f"{pdf_count}.pdf")
                        shutil.move(temp_pdf_path, pdf_save)
                        print(f"File moved to: {pdf_save}")
                    data.append(
                        {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": page_range, "Month": month, "Day": date, "Year": year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title)

            except Exception as error:
                message = f"Error link - {Article_link} : {str(error)}"
                print("Download failed:", Article_title)
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
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
    except Exception as error:
        Error_message = "Error in the site: " + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

    finally:
        driver.quit()
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
            print(f"Temporary directory {download_dir} has been deleted.")
