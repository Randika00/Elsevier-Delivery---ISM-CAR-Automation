import os
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import common_function
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import urllib3
import certifi

url_id = "657092805"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

retry_strategy = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(requests.exceptions.RequestException)
)

session = requests.Session()
session.headers.update(headers)

duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
issue = None
time_prefix = None
today_date = None
ini_path = None

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

@retry_strategy
def fetch_url(url):
    return session.get(url, timeout=10)  # 10 seconds timeout

try:
    url = "https://jamc.ayubmed.edu.pk/jamc/index.php/jamc/issue/archive"
    base_url = "https://jamc.ayubmed.edu.pk/"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_156.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "156"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = fetch_url(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    current_link = soup.find("ul", class_="issues_archive").findAll("div", class_="obj_issue_summary")[1].find("a", class_="title").get("href")

    response = fetch_url(current_link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        all_articles = soup.findAll("div", class_="obj_article_summary")
        Total_count = len(all_articles)

        div_element = soup.find("div", class_="sections").findAll("div", class_="section")

        for single_element in div_element:
            article_link, article_title = None, None
            try:
                article_link_tag = single_element.find("ul", class_="cmp_article_list articles")
                if article_link_tag:
                    article_links = article_link_tag.findAll("h3", class_="title")
                    page_ranges = single_element.findAll("div", class_="pages")

                    for article, page_range_tag in zip(article_links, page_ranges):

                        article_title = article.find("a").text.strip()
                        article_link = article.find("a").get("href")
                        page_range = page_range_tag.text.strip() if page_range_tag else ""

                        vol_issue_info = soup.find("h1").text.strip()
                        match = re.match(r"Vol\. (\d+) No\. (\d+) \((\d{4})\)", vol_issue_info)
                        volume, issue, year = "", "", ""
                        if match:
                            volume = match.group(1) if vol_issue_info else ""
                            issue = match.group(2) if vol_issue_info else ""
                            year = match.group(3) if vol_issue_info else ""

                        supplement_tag = soup.find("h1").text.strip()
                        supplement_match = re.search(r"Suppl (\d+)", supplement_tag)
                        supplement = supplement_match.group(1) if supplement_match else ""

                        article_response = fetch_url(article_link)
                        if article_response.status_code == 200:
                            article_soup = BeautifulSoup(article_response.text, 'html.parser')

                            doi_tag = article_soup.find("div", class_="main_entry").find("span", class_="value")
                            doi = doi_tag.find("a").get("href").replace("https://doi.org/", "") if doi_tag and doi_tag.find("a") else ""

                            last_page_link = article_soup.find("ul", class_="value supplementary_galleys_links").find("li")
                            last_page = last_page_link.find("a", class_="obj_galley_link_supplementary pdf").get('href') if last_page_link else ""

                            if last_page:
                                last_response = fetch_url(last_page)
                                last_soup = BeautifulSoup(last_response.text, "html.parser")

                                pdf_url = last_soup.find("header", class_="header_view").find("a", class_="download").get('href')

                                if not pdf_url:
                                    print(f"This Article '{article_title}' does not have a PDF URL")
                                    continue

                                check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)

                                if Check_duplicate.lower() == "true" and check_value:
                                    message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                    duplicate_list.append(message)
                                    print("Duplicate Article :", article_title)

                                else:
                                    pdf_content = fetch_url(pdf_url).content
                                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                    with open(output_fimeName, 'wb') as file:
                                        file.write(pdf_content)
                                    data.append({
                                        "Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                                        "Volume": volume, "Issue": issue, "Supplement": supplement, "Part": "",
                                        "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "",
                                        "Year": year, "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id
                                    })
                                    df = pd.DataFrame(data)
                                    df.to_excel(out_excel_file, index=False)
                                    pdf_count += 1
                                    scrape_message = f"{article_link}"
                                    completed_list.append(scrape_message)
                                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                        write_file.write(article_link + '\n')
                                    print("Original Article :", article_link)

            except Exception as error:
                message = f"Error link - {article_title} : {str(error)}"
                print(f"{article_title} : {str(error)}")
                error_list.append(message)

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                            str(len(duplicate_list)), str(len(error_list)))
        except Exception as error:
            message = f"Failed to send post request : {str(error)}"
            error_list.append(message)

        try:
            if str(Email_Sent).lower() == "true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list), ini_path, attachment, current_date,
                                                     current_time, Ref_value)
        except Exception as error:
            message = f"Failed to send email : {str(error)}"
            error_list.append(message)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass

except Exception as e:
    Error_message = "Error in the site :" + str(e)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
