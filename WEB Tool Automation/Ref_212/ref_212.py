import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
import os
import common_function
from googletrans import Translator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

url_id = "943736833"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

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

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        pass
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')

try:
    url = "http://eng.jksas.or.kr/"
    toc_url = "http://eng.jksas.or.kr/sub/sub4_03.asp"

    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "Ref_212.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    Ref_value = "212"
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    session = requests_retry_session()

    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    div_element = soup.find("div", id="main02").findAll("table", class_="main_table02")

    Total_count = len(div_element)
    print(f"Total number of articles:{Total_count}", "\n")

    for single_element in div_element:
        article_link, article_title = None, None
        try:
            article_title_div = single_element.find("p")
            if article_title_div:
                article_title = article_title_div.find("strong").text.strip()

                article_link_tag = single_element.findAll("p")[1]
                if article_link_tag:
                    onclick_attribute = article_link_tag.find("a", class_="jbuttn01")
                    if onclick_attribute:
                        onclick_text = onclick_attribute.get('href')
                        article_id = re.search(r'ViewAbstract\((\d+)\)', onclick_text).group(1)

                        actual_base_link = "http://eng.jksas.or.kr/ViewAbstract.asp?idx="
                        article_link = actual_base_link + str(article_id)

                    pdf_link_text = single_element.findAll("p")[1]
                    pdf_id = ""
                    if pdf_link_text:
                        pdf_ids = pdf_link_text.find("a", class_="jbuttn01", string="Full Text PDF").get('href')
                        if pdf_ids:
                            pdf_id = pdf_ids.split("f=")[-1].split('.')[0]

                        pdf_url = f'http://journal2.ksas.or.kr/UPFILE/PUBLICATION_FILE/J2021049/{pdf_id}.pdf'

                        page_range_doi_tag = single_element.find("p")
                        page_range = ""
                        if page_range_doi_tag:
                            page_range_text = page_range_doi_tag.text
                            page_range_match = re.search(r'pp\.\s(\d+-\d+)', page_range_text)
                            if page_range_match:
                                page_range = page_range_match.group(1)

                            doi_tag = page_range_doi_tag.find("a", href=True)
                            doi = ""
                            if doi_tag:
                                doi = doi_tag['href'].replace("http://dx.doi.org/", "")

                            volume_issue_year_info = soup.find("div", class_="subtt01")
                            volume, issue, month, year = "", "", "", ""
                            if volume_issue_year_info:
                                volume_issue_year_text = volume_issue_year_info.text
                                volume_match = re.search(r'Vol\.\s(\d+)', volume_issue_year_text)
                                issue_match = re.search(r'No\.\s(\d+)', volume_issue_year_text)
                                month_year_match = re.search(
                                    r'(January|February|March|April|May|June|July|August|September|October|November|December),\s(\d{4})',
                                    volume_issue_year_text)

                                if volume_match:
                                    volume = volume_match.group(1) if volume_match else "Volume not found"

                                if issue_match:
                                    issue = issue_match.group(1) if issue_match else "Issue not found"

                                if month_year_match:
                                    month = month_year_match.group(1) if month_year_match else "Month not found"
                                    year = month_year_match.group(2) if month_year_match else "Year not found"

                                check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)

                                if Check_duplicate.lower() == "true" and check_value:
                                    message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                    duplicate_list.append(message)
                                    print("Duplicate Article :", article_title)

                                else:
                                    pdf_content = session.get(pdf_url, headers=headers).content
                                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                    with open(output_fimeName, 'wb') as file:
                                        file.write(pdf_content)
                                    data.append(
                                        {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                         "Identifier": "",
                                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                         "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "",
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
            message = f"Error link - {article_title} : {str(error)}"
            print(f"{article_title} : {str(error)}")
            error_list.append(message)

    try:
        try:
            response_en = session.get(toc_url, headers=headers, timeout=30)
            response_en.raise_for_status()
            soup_en = BeautifulSoup(response_en.text, 'html.parser')

            english_heading = "<h1>Table of Contents - English & Korean Version</h1>\n"
            english_content = soup_en.prettify()

        except Exception as e:
            error_message = f"Error processing English version of URL {url}: {str(e)}"
            error_list.append(error_message)
            print(error_message)
            english_heading = "<h1>Error loading English version</h1>\n"
            english_content = f"<p>{error_message}</p>\n"

        combined_content = f"{english_heading}{english_content}"

        # Save combined content to HTML file
        output_file = os.path.join(current_out, f"{url_id}_TOC.html")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(combined_content)

        print(f"Combined file saved: {output_file}")

    except Exception as e:
        print(f"Error in creating the TOC file: {e}")
        error_list.append(f"Error in creating the TOC file: {e}")

    try:
        common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                        str(len(duplicate_list)),
                                        str(len(error_list)))
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
