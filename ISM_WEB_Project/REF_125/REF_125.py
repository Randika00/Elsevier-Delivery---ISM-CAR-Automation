import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd
import zipfile
import os
import shutil
import glob

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def download_xml(url, local_filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(local_filename, 'wb') as file:
        file.write(response.content)

    print(f"Downloaded {local_filename} from {url}")

Total_count=None
attachment=None
current_date=None
current_time=None
ini_path=None
duplicate_list = []
error_list = []
completed_list=[]
data = []
url_id="77481199"
pdf_count=1
xml_count=1
Ref_value="125"

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url = "http://www.j-csam.org/jcsam/home"
try:
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path= os.path.join(os.getcwd(),"REF_125.ini")
    Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
    current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
    out_excel_file=common_function.output_excel_name(current_out)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    TOC_path, TOC_name = common_function.output_TOC_name(current_out)
    with open(TOC_path, 'w', encoding='utf-8') as html_file:
        html_file.write(str(soup))
    current_issue_href=soup.find("li", class_="m").find("ul", class_="sub").find("a").get("href")
    url2="http://www.j-csam.org/"+current_issue_href
    page2 = requests.get(url2, headers=headers)
    soup2 = BeautifulSoup(page2.content, 'html.parser')
    script_tag = soup2.find('script', language='javascript')
    href_match = re.search(r"window\.location\.href='([^']+)'", script_tag.string)
    href = "http://www.j-csam.org/"+href_match.group(1) if href_match else None
    page_3 = requests.get(href, headers=headers)
    soup3 = BeautifulSoup(page_3.content, 'html.parser')
    content_archive = soup3.find_all("div", class_="article_des article_issue_fl")
    Total_count = len(content_archive)
    print(f"Total number of articles:{Total_count}", "\n")
    for div_element in content_archive:
        Article_link = None
        try:
            Article_link = "http://www.j-csam.org/"+div_element.find("div",class_="article_title").find("a").get("href")
            meta_data=div_element.find("p",class_="article_position").get_text(strip=True)
            year_match = re.search(r'(\d{4}),', meta_data)
            volume_match = re.search(r',\s*(\d+)\(', meta_data)
            issue_match = re.search(r'\((\d+)\)', meta_data)
            page_range_match = re.search(r':(\d+-\d+)', meta_data)

            # Extract the matched groups
            year = year_match.group(1) if year_match else None
            volume = volume_match.group(1) if volume_match else None
            issue = issue_match.group(1) if issue_match else None
            page_range = page_range_match.group(1) if page_range_match else None

            doi = div_element.find("p",class_="article_position").find("span").find("a").get_text(strip=True)

            pdf_page = requests.get(Article_link, headers=headers)
            soup2 = BeautifulSoup(pdf_page.content, 'html.parser')
            title = soup2.find("div",class_="en").find('div', class_='title', id='EnTitleValue').text.strip()
            pdf_link="http://www.j-csam.org/"+soup2.find("a",class_="pt1").get("href")
            xml_link="http://www.j-csam.org/"+soup2.find("a",class_="pt3").get("href")
            check_value,tpa_id= common_function.check_duplicate(doi, title, url_id, volume, issue)
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
                output_fileName = os.path.join(current_out, f"{pdf_count}.xml")
                response = requests.get(xml_link)
                with open(output_fileName, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded {output_fileName}")
                data.append(
                    {"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                     "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                     "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                     "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
                pdf_count += 1
                xml_count += 1
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

