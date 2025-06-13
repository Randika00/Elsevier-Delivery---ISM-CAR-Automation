import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

attachment=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
Total_count=None
duplicate_list = []
error_list = []
completed_list=[]
data = []
url_id="939594938"
pdf_count=1


try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

current_datetime = datetime.now()
current_date = str(current_datetime.date())
current_time = current_datetime.strftime("%H:%M:%S")

ini_path= os.path.join(os.getcwd(),"Info.ini")
Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
out_excel_file = common_function.output_excel_name(current_out)
Ref_value="26"

url = "http://www.spgykj.com/en/article/current"
try:
    page = requests.get(url, headers=headers,timeout=10000)
    soup = BeautifulSoup(page.content, 'html.parser')
    TOC_path, TOC_name = common_function.output_TOC_name(current_out)
    with open(TOC_path, 'w', encoding='utf-8') as html_file:
        html_file.write(str(soup))
    meta_tag = soup.find('meta', {'name': 'citation_title'})
    if meta_tag:
        citation_title = meta_tag.get('content')
        split_citation_title = citation_title.split(' ')
        year = split_citation_title[-5]
        volume = split_citation_title[-3]
        issue = split_citation_title[-1]
        content_archives= soup.find_all("div", class_="article-list-right")
        Total_count = len(content_archives)
        print(f"Total number of articles:{Total_count}", "\n")
        for content_archive in content_archives:
            Article_link = None
            try:
                Article_link = 'http://www.spgykj.com' + content_archive.find('div', class_='article-list-title clearfix').find('a').get('href')
                doi_tag = content_archive.find('div', class_='article-list-time')
                if doi_tag:
                    doi = doi_tag.find_next('a').text.strip()
                page_range_tag = content_archive.find('font', string=lambda text: ' ' in text and ':' in text)
                if page_range_tag:
                    page_range = page_range_tag.text.split(':')[-1].strip().replace('.', '')
                    title_tag = content_archive.find('div', class_='article-list-title').find('a')
                    if title_tag:
                        title = title_tag.text.strip()
                    pdf_link_soup=content_archive.find("font",class_="font3").find("a")
                    onclick_value = re.search(r"downloadpdf\('([^']*)'\)", pdf_link_soup.get('onclick')).group(1)
                    base_url = "http://www.spgykj.com/article/exportPdf?id="
                    pdf_link = base_url +onclick_value+"&language=en"
                    check_value,tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print("Duplicate Article :", title)
                    else:
                        print("Original Article :", title)
                        pdf_content = requests.get(pdf_link, headers=headers,timeout=10000).content
                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_fimeName, 'wb') as file:
                            file.write(pdf_content)
                        print(f"Downloaded: {output_fimeName}")
                        data.append({"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                             "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(Article_link)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_link + '\n')

            except Exception as error:
                message = f"Error link - {Article_link} : {str(error)}"
                error_list.append(message)
                print(error)
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)
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
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

finally:
    subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
    error_file_path = os.path.join(current_out, 'download_details.html')
    with open(error_file_path, 'w', encoding='utf-8') as file:
        file.write(error_html_content)
    print("Error details file saved to:", error_file_path)