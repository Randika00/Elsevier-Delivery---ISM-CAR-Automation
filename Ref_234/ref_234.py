import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import common_function

url_id = "949225007"

duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
time_prefix = None
today_date = None
ini_path = None

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

# Set up retry mechanism
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

def get_token(url):
    response = requests.get(url, headers=headers)
    # print("Cookies:", response.cookies)
    cookie = response.cookies
    token = cookie.get("wkxt3_csrf_token")

    if token:
        token = token.replace("-", "")
    else:
        print("Token not found in cookies")
        raise Exception("Token not found in cookies")

    return token

try:
    try:
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
    except FileNotFoundError:
        with open('completed.txt', 'w', encoding='utf-8'):
            pass
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

    base_url = "http://www.zgfsws.com/EN"
    url = "http://www.zgfsws.com/EN/current"
    toc_url = "http://www.zgfsws.com/EN/current"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_234.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "234"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    response = http.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, "html.parser")

    div_element = soup.find("ul", class_="article-list").findAll("div", class_="article-l article-w")

    Total_count = len(div_element)
    print(f"Total number of articles: {Total_count}", "\n")

    for single_element in div_element:
        article_link, article_title = None, None
        try:
            article_title_div = single_element.find("div", class_="j-title-1")
            if article_title_div:
                article_title = article_title_div.find("a").text.strip()
                article_link = article_title_div.find("a").get('href')

                pages_doi_tag = single_element.find("div", class_="j-volumn-doi")
                doi = "", ""
                if pages_doi_tag:
                    doi_tag = pages_doi_tag.find("a", class_="j-doi")
                    doi = doi_tag.get("href").replace("https://doi.org/", "") if doi_tag else ""

                pages_text = single_element.find("div", class_="j-volumn-doi")
                page_range = ""
                if pages_text:
                    pages_tag = pages_text.find("span", class_="j-volumn")
                    if pages_tag:
                        page_range = re.search(r"(\d+-\d+)", pages_tag.text.strip())
                        if page_range:
                            page_range = page_range.group(1) if pages_tag else ""

                    date_volume_issue_text = soup.find("span", class_="n-j-q")
                    day, month, year, volume, issue = "", "", "", "", ""
                    if date_volume_issue_text:
                        date_volume_issue = date_volume_issue_text.text.strip()

                        match = re.search(r"(\d{1,2}) (\w+) (\d{4}) Volume (\d+) Issue (\d+)", date_volume_issue)

                        if match:
                            day = match.group(1) if date_volume_issue else ""
                            month = match.group(2) if date_volume_issue else ""
                            year = match.group(3) if date_volume_issue else ""
                            volume = match.group(4) if date_volume_issue else ""
                            issue = match.group(5) if date_volume_issue else ""
                        else:
                            print("No match found for date, volume, and issue")

                        token = get_token("http://www.zgfsws.com/")
                        pdf_link = f"http://www.zgfsws.com/EN/PDF/{doi}?token={token}"

                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)

                        if Check_duplicate.lower() == "true" and check_value:
                            message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                            duplicate_list.append(message)
                            print("Duplicate Article :", article_title)

                        else:
                            pdf_content = http.get(pdf_link, headers=headers, timeout=30).content
                            output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                            with open(output_fimeName, 'wb') as file:
                                file.write(pdf_content)
                            data.append(
                                {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                 "ItemID": "",
                                 "Identifier": "",
                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                 "Special Issue": "", "Page Range": page_range, "Month": month,
                                 "Day": day,
                                 "Year": year,
                                 "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                 "user_id": user_id, "TOC File Name": f"{url_id}_TOC.html"})
                            df = pd.DataFrame(data)
                            df.to_excel(out_excel_file, index=False)
                            pdf_count += 1
                            scrape_message = f"{article_link}"
                            completed_list.append(scrape_message)
                            with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                write_file.write(article_link + '\n')
                            print("Original Article :", article_link)

        except Exception as error:
            message = f"Error link - {article_title}: {str(error)}"
            print(f"{article_title}: {str(error)}")
            error_list.append(message)

    try:
        try:
            response_en = http.get(toc_url, headers=headers, timeout=30)
            response_en.raise_for_status()
            soup_en = BeautifulSoup(response_en.text, 'html.parser')

            english_heading = "<h1>Table of Contents - English Version</h1>\n"
            english_content = soup_en.prettify()

        except Exception as e:
            error_message = f"Error processing English version of URL {toc_url}: {str(e)}"
            error_list.append(error_message)
            print(error_message)
            english_heading = "<h1>Error loading English version</h1>\n"
            english_content = f"<p>{error_message}</p>\n"

        try:
            url_cn = toc_url.replace('/EN', '/CN')

            response_cn = http.get(url_cn, headers=headers, timeout=30)
            response_cn.raise_for_status()
            soup_cn = BeautifulSoup(response_cn.text, 'html.parser')

            chinese_heading = "<h1>Table of Contents - Chinese Version</h1>\n"
            chinese_content = soup_cn.prettify()

        except Exception as e:
            error_message = f"Error processing Chinese version of URL {toc_url}: {str(e)}"
            error_list.append(error_message)
            print(error_message)
            chinese_heading = "<h1>Error loading Chinese version</h1>\n"
            chinese_content = f"<p>{error_message}</p>\n"

        combined_content = f"{english_heading}{english_content}<hr>{chinese_heading}{chinese_content}"

        output_file = os.path.join(current_out, f"{url_id}_TOC.html")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(combined_content)

        print(f"Combined file saved: {output_file}")

    except Exception as e:
        print(f"Error in creating the TOC file: {e}")
        error_list.append(f"Error in creating the TOC file: {e}")

    try:
        common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                        str(len(duplicate_list)), str(len(error_list)))
    except Exception as error:
        message = f"Failed to send post request: {str(error)}"
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
        message = f"Failed to send email: {str(error)}"
        error_list.append(message)

    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass

except Exception as error:
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
