import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
def get_token(url):
    response = requests.get(url,headers=headers)
    cookie=response.cookies
    token=cookie.get("wkxt3_csrf_token").replace("-","")
    return token

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

url_id = None
attachment = None
current_date = None
current_time = None
ini_path = None
duplicate_list = []
error_list = []
completed_list = []
data = []
pdf_count = 1
Ref_value = "232"

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

chinese_url = "https://www.ahs.ac.cn/CN/0513-353X/home.shtml"
url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        url, url_id = url_list[url_index].split(',')

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "REF_232.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)

        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        TOC_path, TOC_name = common_function.output_TOC_name(current_out)
        with open(TOC_path, 'w', encoding='utf-8') as html_file:
            html_file.write(str(soup))

        content_archive = soup.find_all("ul", class_="lunwen")
        for element in content_archive:
            Article_link = None
            try:
                Article_link = element.find("li",class_="biaoti").find("a").get("href")
                title = element.find("li",class_="biaoti").find("a").get_text(strip=True)

                page2 = requests.get(Article_link, headers=headers)
                soup2 = BeautifulSoup(page2.content, 'html.parser')

                html_content=soup2.find("div",class_="col-md-12").find("p")
                year = soup2.find('a', href=re.compile('showTenYearVolumnDetail\.do\?nian=\d{4}')).text
                volume = re.search(r'\d+', soup2.find("div", class_="col-md-12").find("span").find_all('a')[2].get_text(strip=True)).group()
                issue = re.search(r'\d+', soup2.find("div", class_="col-md-12").find("span").find_all('a')[3].get_text(strip=True)).group()
                page_range = re.search(r'\d+-\d+', soup2.find("div", class_="col-md-12").find("span").get_text(strip=True)).group()
                doi = soup2.find('span', class_='doi-doi').find('a').text

                token = get_token(url)

                pdf_link = f"https://www.ahs.ac.cn/EN/PDF/{doi}?token={token}"
                check_value, tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", title)
                else:
                    session = requests.Session()
                    retries = 0
                    max_retries = 5
                    download_successful = False

                    while retries < max_retries and not download_successful:
                        response = session.post(pdf_link,headers=headers)
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
                            {"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                             "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC": TOC_name})
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
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
            url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the site:" + str(error)
            print(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list), ini_path, attachment, current_date,
                                                 current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                                            len(completed_list), url_id, Ref_value, attachment, current_out)

            url_index, url_check = url_index + 1, 0

    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,
                                                                 completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)

