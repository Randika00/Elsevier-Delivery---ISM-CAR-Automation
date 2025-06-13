import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "www.ajtmh.org",
    "Referer": "https://www.ajtmh.org/contents-by-date.0.shtml",
    "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def extract_csrf_token(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        cookies = response.cookies
        csrf_token_match = re.search(r'wkxt3_csrf_token=([\w-]+)', str(cookies))
        if csrf_token_match:
            csrf_token = csrf_token_match.group(1)
            csrf_token = csrf_token.replace("-", "")
            return csrf_token
        else:
            return "CSRF token not found."
    except Exception as e:
        return f"Error occurred: {str(e)}"


duplicate_list = []
error_list = []
completed_list=[]
data = []
url_id="76212799"
pdf_count=1
Ref_value="187"
attachment=None
current_date=None
current_time=None
ini_path=None

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url = "https://www.ajtmh.org/view/journals/tpmd/110/5/tpmd.110.issue-5.xml"
try:
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path= os.path.join(os.getcwd(),"REF_187.ini")
    Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
    current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
    out_excel_file=common_function.output_excel_name(current_out)

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    year_text=soup.find("h1",class_="typography-body title mb-3 text-headline font-content").get_text(strip=True)
    year_pattern = r'\((\d{4})\)'
    month_pattern = r'\((\w+) \d{4}\)'

    # Search for the patterns in the text
    year_match = re.search(year_pattern, year_text)
    month_match = re.search(month_pattern, year_text)

    # Extract the year and month if the patterns are found
    if year_match and month_match:
        year = year_match.group(0).strip('()')
        month = month_match.group(1)
    else:
        print("Year and/or Month not found")


    content_archive = soup.find_all("div", class_="display-flex flex-col flex-6 flex-nowrap mt-2 mr-2 mb-2 ml-2 pt-2 pr-2 pb-2 pl-2")
    for div_element in content_archive:
        Article_link = None
        try:
            Article_link = "https://www.ajtmh.org"+div_element.find("h1",class_="typography-body text-display4 font-ui fw-3 color-tertiary-dark f-4 ln-3").find("a",class_="c-Button--link").get("href")

            page1 = requests.get(Article_link, headers=headers)
            soup1 = BeautifulSoup(page1.content, 'html.parser')


            title=soup1.find("h1", class_='typography-body title mb-3 text-headline font-content').get_text(strip=True)
            doi_link = soup1.find('dl', class_="doi c-List__items").find('a', {'class': 'c-Button--link'}).get_text(strip=True)
            doi_pattern = r'https://doi.org/([^/]+/[^/]+)'

            # Search for the pattern in the text
            match = re.search(doi_pattern, doi_link)
            if match:
                doi = match.group(1)
            else:
                print("DOI not found")

            volume_text=soup1.find('dl', class_="volumeissue c-List__items").find('a', {'class': 'c-Button--link'}).get_text(strip=True)
            volume_issue_pattern = r'Volume (\d+): Issue (\d+)'
            match = re.search(volume_issue_pattern, volume_text)
            if match:
                volume = match.group(1)
                issue = match.group(2)
            else:
                print("Volume and Issue not found")

            page_range=soup1.find('dl', class_="pagerange c-List__items").find_all('span')[1].get_text(strip=True)

            pdf_link="https://www.ajtmh.org"+soup1.find('a',class_="c-Button c-Button--secondary c-Button--small c-Button--outlined c-Button--full content-download pdf-download").get("href")

            check_value,tpa_id= common_function.check_duplicate(doi, title, url_id, volume, issue)
            if Check_duplicate.lower()=="true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", title)
            else:
                session = requests.Session()
                retries = 0
                max_retries = 5
                download_successful = False

                while retries < max_retries and not download_successful:
                    response = session.post(pdf_link, headers=headers)
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
                        {"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "", "Year": year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", title)
        except Exception as error:
            message = f"Error link - {Article_link} : {str(error)}"
            error_list.append(message)
            print(error)
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
    Error_message = "Error in the site :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)

finally:
    subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
    error_file_path = os.path.join(current_out, 'download_details.html')
    with open(error_file_path, 'w', encoding='utf-8') as file:
        file.write(error_html_content)
    print("Error details file saved to:", error_file_path)

