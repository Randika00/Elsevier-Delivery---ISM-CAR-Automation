import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

Total_count=None
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
# def extract_metadata(text):
#     volume_pattern = r'Vol\.(\d+)'
#     page_range_pattern = r'pp\.\s(\d+-\d+)'
#     year_pattern = r'\b(20\d{2})\b'
#     doi_pattern = r'DOI:\s*([\d\.\/a-z]+)'
#
#     # Extract volume, page range, year, and DOI using regular expressions
#     volume_match = re.search(volume_pattern, text)
#     page_range_match = re.search(page_range_pattern, text)
#     year_match = re.search(year_pattern, text)
#     doi_match = re.search(doi_pattern, text)
#
#     # Check if matches are found and extract the values
#     volume = volume_match.group(1) if volume_match else None
#     page_range = page_range_match.group(1) if page_range_match else None
#     year = year_match.group(1) if year_match else None
#     doi = doi_match.group(1) if doi_match else None
#
#     return volume, page_range, year, doi

def extract_pdf_links(soup):
    li_tags = soup.find("div", class_="gengduo").find_all('li')

    for li in li_tags:
        a_tag = li.find('a')
        if a_tag and ('PDF' in a_tag.text or 'PDF' in a_tag.img['alt']):
            return a_tag['href']

    return None

def extract_metadata_issue(text):
    # Define the regular expression patterns to match volume, page range, year, and DOI
    volume_pattern = r'Vol\.(\d+)'
    issue_pattern = r'No\.(\d+)'
    page_range_pattern = r'pp\.\s(\d+-\d+)'
    year_pattern = r'\b(20\d{2})\b'  # Assuming the year is in the 21st century
    doi_pattern = r'DOI:\s*([\d\.\/a-z]+)'

    # Extract volume, page range, year, and DOI using regular expressions
    volume_match = re.search(volume_pattern, text)
    issue_match = re.search(issue_pattern, text)
    page_range_match = re.search(page_range_pattern, text)
    year_match = re.search(year_pattern, text)
    doi_match = re.search(doi_pattern, text)

    # Check if matches are found and extract the values
    volume = volume_match.group(1) if volume_match else None
    issue = issue_match.group(1) if issue_match else ""
    page_range = page_range_match.group(1) if page_range_match else None
    year = year_match.group(1) if year_match else None
    doi = doi_match.group(1) if doi_match else None

    return volume, issue,page_range, year, doi

headers = {
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "Connection": "keep-alive",
    "Content-Encoding": "gzip",
    "Content-Type": "text/html; charset=UTF-8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "_ga=GA1.1.287552364.1710735376; ci_session=01n0crh61kgc4oq78fiflfksm3102qc2; _ga_PD3QTEE3HW=GS1.1.1710821323.2.1.1710821423.25.0.0; _ga_G5TCNFJCYP=GS1.1.1710821423.2.0.1710821423.0.0.0",
    "Host": "www.techscience.com",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
pdf_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
url_info_list=[]
with open('urlDetails.txt', 'r') as file:
    for line in file:
        url,url_id = line.strip().split(',')
        url_info_list.append({"url": url, "url_id": url_id})

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

for url_info in url_info_list:
    try:
        url = url_info["url"]
        url_id = url_info["url_id"]
        pdf_count = 1
        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        user_id = os.getlogin()

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "REF_92.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        Ref_value = "92"
        print(url_id)
        page = requests.get(url, headers=headers,timeout=100000)
        soup = BeautifulSoup(page.content, 'html.parser')
        all_issues =soup.find("div",id="con_two_1").find_all('div', class_='bq2')
        Total_count = len(all_issues)
        print(f"Total number of articles:{Total_count}", "\n")
        for issue in all_issues:
            Article_link = None
            try:
                Article_link=issue.find('a').get("href")
                Article_title=issue.find('a').get_text(strip=True)
                text = issue.find('p').get_text(strip=True)
                volume, issue, page_range, year, doi = extract_metadata_issue(text)
                pdf_page = requests.get(Article_link, headers=headers,timeout=100000)
                pdf_soup = BeautifulSoup(pdf_page.content, 'html.parser')
                # pdf_page_url = pdf_soup.find("div", class_="gengduo").find_all('a')[-1].get('href')
                pdf_page_url=extract_pdf_links(pdf_soup)
                pdf_link_page = requests.get(pdf_page_url, headers=headers,timeout=100000)
                pdf_link_soup = BeautifulSoup(pdf_link_page.content, 'html.parser')
                pdf_link = pdf_link_soup.find('div', id="download").find('a')['href']
                check_value,tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, "")
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)
                else:
                    print("Original Article :", Article_title)
                    session = requests.Session()
                    session.headers.update(pdf_headers)
                    retries = 0
                    max_retries = 50
                    download_successful = False

                    while retries < max_retries and not download_successful:
                        try:
                            response = session.get(pdf_link,timeout=100000)
                            pdf_content = response.content

                            output_file_name = os.path.join(current_out, f"{pdf_count}.pdf")
                            with open(output_file_name, 'wb') as file:
                                file.write(pdf_content)

                            if os.path.getsize(output_file_name) > 0:
                                print(f"Downloaded: {output_file_name}")
                                download_successful = True
                            else:
                                retries += 1
                                print(f"Retrying download... Attempt {retries}/{max_retries}")

                        except Exception as e:
                            retries += 1
                            print(f"An error occurred: {e}. Retrying download... Attempt {retries}/{max_retries}")


                    # print(f"Downloaded: {output_file_name}")
                    if download_successful:
                        data.append(
                            {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "","Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                             "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_link + '\n')
                    else:
                        print("Failed to download the PDF after several attempts.")
            except Exception as error:
                message = f"Error link - {Article_link} : {str(error)}"
                error_list.append(message)
                print(error)
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
    except Exception as error:
        Error_message = "Error in the site :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)