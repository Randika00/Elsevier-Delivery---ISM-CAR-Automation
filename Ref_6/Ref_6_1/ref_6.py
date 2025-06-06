import requests
from bs4 import BeautifulSoup
import common_function
import os
import re
from datetime import datetime
from openpyxl import Workbook

ini_path = os.path.join(os.getcwd(), "Ref_6.ini")
Ref_value = '6'
Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-Ch-Ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?1",
    "Sec-Ch-Ua-Platform": "\"Android\""
}

volume_pattern = re.compile(r'Volume\s*(\w+\.?\w*)', re.IGNORECASE)
issue_pattern = re.compile(r'Issue\s*(\w+\.?\w*)', re.IGNORECASE)
pages_pattern = re.compile(r'Pages\s*([\w_]+(?:-\w+)?|\d+(?:-\d+)?)', re.IGNORECASE)
published_pattern = re.compile(r'Published:\s*(?:(\w+)\s+(\d{1,2}),\s*(\d{4})|(\d{4}))', re.IGNORECASE)

filename = 'completed_list.txt'

try:
    with open(filename, 'r') as file:
        completed_list = [line.strip() for line in file]
except FileNotFoundError:
    with open(filename, 'w') as file:
        pass
    completed_list = []

file_path = 'Ref_6.txt'

url_ref_pairs = []

with open(file_path, "r") as file:
    for line in file:
        url, ref = line.strip().split(', ')
        url_ref_pairs.append((url, ref))

for url, ref_no in url_ref_pairs:
    errors = []
    current = []
    duplicate_list = []
    completed = []
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")
    current_out = common_function.return_current_outfolder(Download_Path, user_id, ref_no)
    out_excel_file = common_function.output_excel_name(current_out)
    print(f"URL: {url} - Ref Number: {ref_no}")

    response = requests.get(url, headers=headers)

    articles = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ul_list = soup.find_all('ul', class_='search-resultslisting')

        articles = []

        for ul in ul_list:
            items = ul.find_all('li')
            for item in items:
                article_info = {}

                title_div = item.find('div', class_='searchlist-title')
                if title_div and title_div.a:
                    article_info['title'] = title_div.a.get_text(strip=True)

                try:
                    div_tag = item.find('div', class_='searchlist-doi')

                    if div_tag:
                        a_tag = div_tag.find('a', class_='bluelink-style')
                        if a_tag:
                            href_link = a_tag.get('href')
                            article_info['DOI'] = href_link.replace("https://doi.org/", "")
                        else:
                            errors.append(f"DOI was not found for {article_info['title']} in {ref_no}")
                            article_info['DOI'] = None
                    else:
                        errors.append(f"DOI was not found for {article_info['title']} in {ref_no}")
                        article_info['DOI'] = None
                except AttributeError:
                    errors.append(f"DOI was not found for {article_info['title']} in {ref_no}")
                    article_info['DOI'] = None

                info_div = item.find('div', class_='searchlist-additional-info')
                if info_div:
                    info_text = info_div.get_text(separator=' ')

                    volume_match = volume_pattern.search(info_text)
                    if volume_match:
                        article_info['Volume'] = volume_match.group(1)
                    else:
                        article_info['Volume'] = None

                    issue_match = issue_pattern.search(info_text)
                    if issue_match:
                        article_info['Issue'] = issue_match.group(1)
                    else:
                        article_info['Issue'] = None

                    pages_match = pages_pattern.search(info_text)
                    if pages_match:
                        article_info['Page Range'] = pages_match.group(1)
                    else:
                        article_info['Page Range'] = None

                    published_match = published_pattern.search(info_text)
                    if published_match:
                        if published_match.group(4):
                            article_info['Year'] = published_match.group(4)
                            article_info['Month'] = None
                            article_info['Date'] = None
                        else:
                            article_info['Month'] = published_match.group(1)
                            article_info['Date'] = published_match.group(2)
                            article_info['Year'] = published_match.group(3)

                    pdf_link = item.find('a', string='Download PDF')
                    if pdf_link:
                        article_info['pdf_url'] = pdf_link['href']

                if article_info:
                    articles.append(article_info)
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        errors.append(f"Failed to retrieve the webpage for reference no : {ref_no}")

    for article in articles:
        print(article)
        print("-" * 80)

    if len(articles) == 0:
        errors.append(f"No articles were found for the ref : {ref_no}")

    wb = Workbook()
    ws = wb.active
    ws.title = "Publications"
    column_headers = [
        'Title', 'DOI', 'Publisher Item Type', 'Identifier', 'Volume', 'Issue',
        'Supplement', 'Part', 'Special Issue', 'Page Range', 'Month', 'Day', 'Year',
        'URL', 'SOURCE File Name', 'user_id'
    ]
    ws.append(column_headers)
    iterating_pdf = 1
    pdf_count = 0

    Total_count = len(articles)
    print(f"Total number of articles:{Total_count}", "\n")

    for article in articles:
        output_fileName = os.path.join(current_out, f"{pdf_count + 1}.pdf")
        check_value, tpa_id = common_function.check_duplicate(article['DOI'], article['title'], ref_no, None, article['Issue'])
        if Check_duplicate.lower() == "true" and check_value:
            message = f"{article['pdf_url']} - duplicate record with TPAID : {tpa_id}"
            duplicate_list.append(article['pdf_url'])
            print("Duplicate Article :", article['pdf_url'])
        elif article['pdf_url'] in completed_list:
            print(f"The pdf was downloaded already {article['pdf_url']}")
            errors.append(f"The pdf was downloaded already {article['pdf_url']}")

        else:
            response = requests.get(article['pdf_url'], stream=True, headers=headers)
            if response.status_code == 200:
                with open(output_fileName, 'wb') as f:
                    f.write(response.content)

                pdfname = os.path.basename(output_fileName)
                pdf_count += 1
                row_data = [
                    article['title'] if article['title'] else None,
                    article['DOI'] if article['DOI'] else None,
                    None,
                    None,
                    article['Volume'] if article['Volume'] is not None else None,
                    article['Issue'] if article['Issue'] is not None else None,
                    None,
                    None,
                    None,
                    article['Page Range'] if article['Page Range'] is not None else None,
                    article['Month'] if article['Month'] is not None else None,
                    article['Date'] if article['Date'] is not None else None,
                    article['Year'] if article['Year'] else None,
                    article['pdf_url'] if article['pdf_url'] else None,
                    pdfname if article['pdf_url'] else None,
                    user_id
                ]
                ws.append(row_data)
                try:
                    wb.save(out_excel_file)
                    completed.append(article['pdf_url'])
                    completed_list.append(article['pdf_url'])
                except RuntimeError:
                    errors.append(f"No excel file was created for the ref no: {ref_no} for iteration : {pdf_count}")
                    print(f"error in creating the excel file for {article['pdf_url']} for iteration {iterating_pdf}")
                print(f"Downloaded: {article['pdf_url']}")

            else:
                print(f"Failed to download PDF for DOI: {article['DOI']} in {ref_no}")
                errors.append(f"Failed to download PDF for DOI: {article['DOI']} in {ref_no}")

    print(completed)
    print(errors)

    try:
        common_function.sendCountAsPost(ref_no, Ref_value, str(Total_count), str(len(completed)),
                                        str(len(duplicate_list)),
                                        str(len(errors)))
    except Exception as error:
        message = f"Failed to send post request : {str(error)}"
        errors.append(message)

    try:
        if str(Email_Sent).lower() == "true":
            attachment_path = out_excel_file
            if os.path.isfile(attachment_path):
                attachment = attachment_path
            else:
                attachment = None
            common_function.attachment_for_email(ref_no, duplicate_list, errors, completed,
                                                 len(completed), ini_path, attachment, current_date,
                                                 current_time, Ref_value)
    except Exception as error:
        message = f"Failed to send email : {str(error)}"
        errors.append(message)

    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass

    try:
        with open(filename, 'w') as file:
            for item in completed_list:
                file.write(f"{item}\n")
        print("Data written back to the file successfully.")
    except Exception as e:
        print(f"An error occurred while writing back to the file: {e}")
