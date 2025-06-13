import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "sf1970.cnif.cn",
    "If-Modified-Since": "Thu, 09 May 2024 04:04:41 GMT",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
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

Total_count=None
attachment=None
current_date=None
current_time=None
ini_path=None
duplicate_list = []
error_list = []
completed_list=[]
data = []
url_id="947033206"
pdf_count=1
Ref_value="14"


try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url = "http://sf1970.cnif.cn/EN/0253-990X/current.shtml"
try:
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path= os.path.join(os.getcwd(),"REF_14.ini")
    Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
    current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
    out_excel_file=common_function.output_excel_name(current_out)

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    date_element = soup.find("h3", class_="latest-issue").text.strip()
    date_components = date_element.split(", Volume ")
    date_info = date_components[0]
    volume_info = date_components[1]
    day, month, year = [info.strip() for info in date_info.split()]
    volume, issue = [info.strip() for info in volume_info.split(" Issue ")]
    content_archive = soup.find_all("li", class_="noselectrow")
    Total_count = len(content_archive)
    print(f"Total number of articles:{Total_count}", "\n")
    for div_element in content_archive:
        Article_link = None
        try:
            Article_link = div_element.find("a").get("href")
            page_content = requests.get(Article_link, headers=headers)
            soup_content = BeautifulSoup(page_content.content, 'html.parser')
            title=soup_content.find("p", class_='main_content_top_title').get_text(strip=True)
            doi = soup_content.find('div', class_="main_content_top_div").find_all('a',class_="main_content_top_div_a")[-1].get_text(strip=True)
            page_range_text = soup_content.find_all("span",class_="main_content_top_div_span")[-2].get_text(strip=True)
            pattern = r'\d+-\d+'
            matches = re.findall(pattern, page_range_text)
            if matches:
                page_range = matches[0]
            base_url = "http://sf1970.cnif.cn/EN/PDF/"
            pdf_link=base_url+doi+f"?token={extract_csrf_token(url)}.pdf"
            check_value,tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
            if Check_duplicate.lower()=="true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", title)
            else:
                print("Original Article :", title)
                session = requests.Session()
                pdf_content = session.get(pdf_link, headers=headers).content
                output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                with open(output_fileName, 'wb') as file:
                    file.write(pdf_content)
                print(f"Downloaded: {output_fileName}")
                data.append(
                    {"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                     "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                     "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "", "Year": year,
                     "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
                pdf_count += 1
            if not Article_link in read_content:
                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                    write_file.write(Article_link + '\n')
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
        common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)
    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass
except Exception as error:
    Error_message = "Error in the site :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)

