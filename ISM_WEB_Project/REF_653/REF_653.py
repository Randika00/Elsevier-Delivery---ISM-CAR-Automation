import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pandas as pd
import common_function

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

def get_soup(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def print_bordered_message(message):
    border_length = len(message) + 4
    border = "-" * (border_length - 2)

    print(f"+{border}+")
    print(f"| {message} |")
    print(f"+{border}+")
    print()

def get_ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

duplicate_list = []
error_list = []
completed_list = []
attachment = None
url_id = None
current_date = None
current_time = None
Ref_value = None
ini_path = None
Total_count = None

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

try:
    with open('urlDetails.txt', 'r', encoding='utf-8') as file:
        url_list = file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\" : " + str(error)
    print_bordered_message(Error_message)
    error_list.append(Error_message)
    # Assuming common_function is defined elsewhere
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        print_bordered_message("Process started...")
        print("This may take some time. Please wait..........")
        url, url_id = url_list[url_index].split(',')
        print(f"Executing this {url}")

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "REF_653.ini")
            # Assuming common_function is defined elsewhere
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "653"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1
        url_value = url.split('/')[-3]

        soup = get_soup(url)

        current_href = soup.find('dl', id="acMenu").find('div', id="d_ti").find('a').get('href')
        current_soup = get_soup(current_href)

        text = current_soup.find('section', id="section1").find("h1").get_text(strip=True)
        pattern = r'Volume (\d+) Issue (\d+) \(\s*(\w+)\s+(\d{4})\s*\)'

        match = re.search(pattern, text)
        if match:
            volume = match.group(1)
            issue = match.group(2)
            month = match.group(3)
            year = match.group(4)

            # Print the results
            print(f'volume="{volume}", issue="{issue}", month="{month}", year="{year}"')
        else:
            print("No match found")

        hr_tags = current_soup.find_all('hr')
        extracted_data = []
        for i in range(len(hr_tags) - 1):
            content = []
            for element in hr_tags[i].find_all_next():
                if element == hr_tags[i + 1]:
                    break
                content.append(element)
            extracted_data.append(content)

        Total_count = len(hr_tags) - 1
        print(f"Total number of articles: {Total_count}", "\n")

        for i in range(len(hr_tags) - 1):
            try:
                content = extracted_data[i]

                article_title = None
                pdf_link = None
                page_range = ""

                # Extract article title, page range, and PDF link
                for elem in content:
                    try:
                        if elem.name == 'h3':
                            article_title = elem.get_text(strip=True)
                        elif elem.name == 'div' and 'paged' in elem.get('class', []):
                            page_text = elem.get_text(strip=True)
                            match = re.search(r'Pages (\d+-\d+)', page_text)
                            if match:
                                page_range = match.group(1)
                            else:
                                page_range = ""
                        elif elem.name == 'div' and 'fulltext' in elem.get('class', []):
                                pdf_link = elem.find('a', href=True)['href']
                    except Exception as e:
                        print(f"An error occurred while processing the element: {elem}")
                        print(f"Error: {str(e)}")
                        print_bordered_message(Error_message)
                        error_list.append(Error_message)
                        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)
                        common_function.email_body_html(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value,attachment, current_out)
                        continue

                if article_title and pdf_link:
                    print(f"Article Title: {article_title}")
                    print(f"PDF Link: {pdf_link}")
                    print(f"Page Range: {page_range}")
                    check_value, tpa_id = common_function.check_duplicate("", article_title, url_id, volume, issue)
                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{pdf_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print_bordered_message(f"Duplicate Article: {article_title}")
                    else:
                        session = requests.Session()
                        retries = 0
                        max_retries = 5
                        download_successful = False

                        while retries < max_retries and not download_successful:
                            response = session.get(pdf_link, headers=headers)
                            pdf_content = response.content

                            output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                            with open(output_fileName, 'wb') as file:
                                file.write(pdf_content)

                            if os.path.getsize(output_fileName) > 0:
                                print(f"Downloaded: {output_fileName}")
                                download_successful = True
                            else:
                                retries += 1
                                print(f"Retrying download... Attempt {retries}/{max_retries}")

                        if download_successful:
                            data.append(
                                {"Title": article_title, "DOI": "", "Publisher Item Type": "", "ItemID": "",
                                 "Identifier": "",
                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                 "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                                 "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                            df = pd.DataFrame(data)
                            df.to_excel(out_excel_file, index=False)
                            pdf_count += 1
                            scrape_message = f"{pdf_link}"
                            completed_list.append(scrape_message)
            except Exception as error:
                message = f"Error link - {pdf_link} : {str(error)}"
                print_bordered_message(f"Download failed: {article_title}")
                error_list.append(message)

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)), str(len(error_list)))
        except Exception as error:
            message = str(error)
            error_list.append(message)

        if str(Email_Sent).lower() == "true":
            attachment_path = out_excel_file
            if os.path.isfile(attachment_path):
                attachment = attachment_path
            else:
                attachment = None
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list, len(completed_list), url_id, Ref_value, attachment, current_out)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the site:" + str(error)
            print_bordered_message(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list, len(completed_list), url_id, Ref_value, attachment, current_out)
            url_index, url_check = url_index + 1, 0
