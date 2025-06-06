import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import common_function  # Assuming this is your custom module for common functions

# Define constants or configuration variables
url_id = "657092713"
Ref_value = "260"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

# Configure retry strategy for requests
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

# Initialize lists and variables
duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
today_date = None
ini_path = None

try:
    # Ensure 'completed.txt' exists and read its content
    try:
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
    except FileNotFoundError:
        with open('completed.txt', 'w', encoding='utf-8'):
            pass
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

    # Example base URL and URL to scrape
    base_url = "https://www.hxkqyxzz.net/EN/"
    url = "https://www.hxkqyxzz.net/EN/1000-1182/current.shtml"

    # Get current date and time
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    # Example path to configuration file
    ini_path = os.path.join(os.getcwd(), "Ref_260.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)
    print(url_id)

    duplicate_list = []
    error_list = []
    completed_list = []
    data = []
    pdf_count = 1

    # Send HTTP GET request to retrieve webpage content
    response = http.get(url, headers=headers, timeout=30)
    response.raise_for_status()  # Raise error for bad responses

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all articles in the webpage
    div_element = soup.find("div", class_="articles").findAll("div", class_="noselectrow")
    Total_count = len(div_element)
    # print(f"Total number of articles:{Total_count}", "\n")

    # Loop through each article element
    for single_element in div_element:
        article_link, article_title = None, None
        try:
            # Extract article title and link
            article_title_div = single_element.find("div", class_="col-md-12 col-sm-12 col-xs-12")
            if article_title_div:
                article_title = article_title_div.find("dd").find("a").text.strip()
                article_link = article_title_div.find("dd").find("a").get('href')

                # Extract volume and issue information
                volume_issue_info = single_element.find("dd", class_="kmnjq")
                volume, issue = "", ""
                if volume_issue_info:
                    volume_issue_text = volume_issue_info.text.strip()
                    match = re.search(r'(\d+)\((\d+)\)', volume_issue_text)
                    if match:
                        volume = match.group(1)
                        issue = match.group(2)

                # Extract day, month, year information
                day_month_year_info = soup.find("div", class_="njq")
                day, month, year = "", "", ""
                if day_month_year_info:
                    day_month_year_text = day_month_year_info.text.strip()
                    date_match = re.search(r'(\d{2}) (\w+) (\d{4})', day_month_year_text)
                    if date_match:
                        day = date_match.group(1)
                        month = date_match.group(2)
                        year = date_match.group(3)

                # Extract page range and DOI information
                page_ranges_doi_tag = single_element.find("dd", class_="kmnjq")
                page_range, doi = "", ""
                if page_ranges_doi_tag:
                    page_ranges_doi_text = page_ranges_doi_tag.text.strip()
                    page_range_match = re.search(r'(\d+-\d+)', page_ranges_doi_text)
                    doi_match = re.search(r'doi:<a href="https://doi.org/([\d.]+/[\w.]+)"', str(page_ranges_doi_tag))

                    if page_range_match:
                        page_range = page_range_match.group(1)
                    if doi_match:
                        doi = doi_match.group(1)

                # Extract PDF download link
                onclick_attr = single_element.find("dd", class_="zhaiyao")
                pdf_id = ""
                if onclick_attr:
                    onclick_text = onclick_attr.find("a", string="PDF（pc）").get('onclick')
                    pdf_id_match = re.search(r'lsdy1\([\'"]PDF[\'"],[\'"](\d+)[\'"]', onclick_text)
                    if pdf_id_match:
                        pdf_id = pdf_id_match.group(1)

                    base_pdf_url = "https://www.hxkqyxzz.net/EN/article/downloadArticleFile.do?attachType=PDF&id="
                    pdf_link = base_pdf_url + str(pdf_id)

                    # Check for duplicate articles
                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)
                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print("Duplicate Article :", article_title)
                    else:
                        pdf_content = http.get(pdf_link, headers=headers, timeout=10).content
                        output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_fileName, 'wb') as file:
                            file.write(pdf_content)

                        # Append data to list for DataFrame and Excel output
                        data.append({
                            "Title": article_title,
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
                            "Day": day,
                            "Year": year,
                            "URL": article_link,
                            "SOURCE File Name": f"{pdf_count}.pdf",
                            "user_id": user_id,
                            "TOC File Name": f"{url_id}_TOC.html"
                        })

                        # Create DataFrame and save to Excel
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)

                        # Increment PDF count and append to completed list
                        pdf_count += 1
                        scrape_message = f"{article_link}"
                        completed_list.append(scrape_message)

                        # Append processed article link to 'completed.txt'
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(article_link + '\n')

                        print("Original Article :", article_link)

        except Exception as error:
            message = f"Error link - {article_title} : {str(error)}"
            print(f"{article_title} : {str(error)}")
            error_list.append(message)

    # Attempt to generate combined HTML file for English and Chinese versions
    try:
        try:
            response_en = requests.get(url)
            response_en.raise_for_status()
            soup_en = BeautifulSoup(response_en.text, 'html.parser')

            english_heading = "<h1>Table of Contents - English Version</h1>\n"
            english_content = soup_en.prettify()

        except Exception as e:
            error_message = f"Error processing English version of URL {url}: {str(e)}"
            error_list.append(error_message)
            print(error_message)
            english_heading = "<h1>Error loading English version</h1>\n"
            english_content = f"<p>{error_message}</p>\n"

        try:
            url_cn = url.replace('/EN', '/CN')

            response_cn = requests.get(url_cn)
            response_cn.raise_for_status()
            soup_cn = BeautifulSoup(response_cn.text, 'html.parser')

            chinese_heading = "<h1>Table of Contents - Chinese Version</h1>\n"
            chinese_content = soup_cn.prettify()

        except Exception as e:
            error_message = f"Error processing Chinese version of URL {url}: {str(e)}"
            error_list.append(error_message)
            print(error_message)
            chinese_heading = "<h1>Error loading Chinese version</h1>\n"
            chinese_content = f"<p>{error_message}</p>\n"

        combined_content = f"{english_heading}{english_content}<hr>{chinese_heading}{chinese_content}"

        # Save combined content to HTML file
        output_file = os.path.join(current_out, f"{url_id}_TOC.html")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(combined_content)

        print(f"Combined file saved: {output_file}")

    except Exception as e:
        print(f"Error in creating the TOC file : {e}")
        error_list.append(f"Error in creating the TOC file : {e}")

    # Attempt to send count as post request
    try:
        common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                        str(len(duplicate_list)),
                                        str(len(error_list)))
    except Exception as error:
        message = f"Failed to send post request : {str(error)}"
        error_list.append(message)

    # Attempt to send email if enabled
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

    # Create a 'Completed.sts' file
    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w'):
        pass

except Exception as e:
    Error_message = "Error in the site :" + str(e)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)

# End of the main script

