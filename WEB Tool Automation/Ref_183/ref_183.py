import os
import re
import requests
import pandas as pd
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime
import common_function
import fitz  # PyMuPDF
from tenacity import retry, stop_after_attempt, wait_exponential

source_id = "942655775"

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

def find_element(elements, indices):
    for index in indices:
        try:
            return elements[index]
        except IndexError:
            continue
    return None

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))  # Retry with exponential backoff
def fetch_url(url, headers, timeout=60):
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response

def extract_page_range_from_pdf(pdf_url):
    try:
        response = fetch_url(pdf_url, headers={})
        pdf_data = response.content
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):  # Check all pages
            text += pdf_document.load_page(page_num).get_text()

        match = re.search(r"Eur J Clin Exp Med \d{4}; \d{2} \(\d\): (\d+–\d+)", text)
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f"Error extracting page range from {pdf_url}: {e}")
        return None

try:
    try:
        with open('urlDetails.txt', 'r', encoding='utf-8') as file:
            url_details = file.readlines()
    except Exception as error:
        Error_message = f"Error in the urlDetails.txt file: {error}"
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                             ini_path, attachment, current_date, current_time, Ref_value)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    try:
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
    except FileNotFoundError:
        with open('completed.txt', 'w', encoding='utf-8'):
            with open('completed.txt', 'r', encoding='utf-8') as read_file:
                read_content = read_file.read().split('\n')

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://www.ejcem.ur.edu.pl"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_183.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "183"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = fetch_url(url, headers=headers)
            link = BeautifulSoup(response.content, "html.parser").find("ul", class_="menu nav").findAll("li",
                                                                                                         class_="leaf")[1].find("a").get("href")

            current_link = base_url + link

            response = fetch_url(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                span_element = soup.find("span", class_="field-content").findAll("article",
                                                                                 class_="node node-wpis-publikacji node-promoted clearfix")

                Total_count = len(span_element)
                # print(f"Total number of articles: {Total_count}", "\n")

                for single_element in span_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("div", class_="field-item even")
                        if article_title_div:
                            article_title = article_title_div.find("span").find("a").text.strip()
                            article_links = article_title_div.find("span").find("a").get('href')
                            article_link = urllib.parse.urljoin(base_url, article_links)

                            volume_issue_year_info = soup.find("h2", class_="field-content")
                            year, volume, issue = "", "", ""
                            if volume_issue_year_info:
                                volume_issue_year_text = volume_issue_year_info.text.strip()
                                match = re.match(r"(\d{4}), vol\. (\d+), no\.(\d+)", volume_issue_year_text)
                                if match:
                                    year, volume, issue = match.groups()

                            pdf_url_tag = single_element.find("span", class_="file")
                            pdf_url, page_range = "", ""
                            if pdf_url_tag:
                                pdf_url = pdf_url_tag.find("a").get('href')
                                if pdf_url:
                                    page_range = extract_page_range_from_pdf(pdf_url)

                                article_response = fetch_url(article_link, headers=headers)
                                if article_response.status_code == 200:
                                    article_soup = BeautifulSoup(article_response.text, 'html.parser')

                                    page_ranges_doi_tag = find_element(article_soup.findAll("p", class_="rtejustify"), [6, 5])
                                    if page_ranges_doi_tag:
                                        doi = ""
                                        page_ranges_doi_text = page_ranges_doi_tag.text.strip()
                                        page_range_match = re.search(r"(\d{3}–\d{3})", page_ranges_doi_text)
                                        doi_match = re.search(r"doi: (10\.\d{4,9}/[-._;()/:A-Z0-9]+)", page_ranges_doi_text, re.IGNORECASE)

                                        doi = doi_match.group(1).rstrip('.') if doi_match else ""

                                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                        if Check_duplicate.lower() == "true" and check_value:
                                            message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                            duplicate_list.append(message)
                                            print("Duplicate Article:", article_title)

                                        else:
                                            pdf_content = fetch_url(pdf_url, headers=headers).content
                                            output_file_name = os.path.join(current_out, f"{pdf_count}.pdf")
                                            with open(output_file_name, 'wb') as file:
                                                file.write(pdf_content)
                                            data.append(
                                                {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                 "ItemID": "",
                                                 "Identifier": "",
                                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                 "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "",
                                                 "Year": year,
                                                 "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                                 "user_id": user_id})
                                            df = pd.DataFrame(data)
                                            df.to_excel(out_excel_file, index=False)
                                            pdf_count += 1
                                            scrape_message = f"{article_link}"
                                            completed_list.append(scrape_message)
                                            with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                                write_file.write(article_link + '\n')
                                            print("Original Article:", article_link)

                    except Exception as error:
                        message = f"Error link - {article_title}: {error}"
                        print(f"{article_title}: {error}")
                        error_list.append(message)

                try:
                    common_function.sendCountAsPost(source_id, Ref_value, str(Total_count), str(len(completed_list)),
                                                    str(len(duplicate_list)),
                                                    str(len(error_list)))
                except Exception as error:
                    message = f"Failed to send post request: {error}"
                    error_list.append(message)

                try:
                    if str(Email_Sent).lower() == "true":
                        attachment_path = out_excel_file
                        if os.path.isfile(attachment_path):
                            attachment = attachment_path
                        else:
                            attachment = None
                        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
                                                             len(completed_list), ini_path, attachment, current_date,
                                                             current_time, Ref_value)
                except Exception as error:
                    message = f"Failed to send email: {error}"
                    error_list.append(message)

                sts_file_path = os.path.join(current_out, 'Completed.sts')
                with open(sts_file_path, 'w') as sts_file:
                    pass

        except Exception as e:
            Error_message = "Error in the site :" + str(e)
            print(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except Exception as error:
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
