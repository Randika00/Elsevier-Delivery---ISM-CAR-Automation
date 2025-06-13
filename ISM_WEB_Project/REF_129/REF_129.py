import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}
Total_count=None
duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None

url_id = "77882399"

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url="https://wulixb.iphy.ac.cn/en/custom/current"

try:
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    ini_path = os.path.join(os.getcwd(), "REF_129.ini")
    Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
    current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
    out_excel_file = common_function.output_excel_name(current_out)

    Ref_value = "129"

    duplicate_list = []
    error_list = []
    completed_list=[]
    data = []
    pdf_count = 1

    current_soup=get_soup(url)

    header_text = current_soup.find("div",class_="clearfix coverwrap comwrap").find('h2').text
    volume_issue_year = header_text.strip().split()
    volume = volume_issue_year[1].replace(',', '')
    issue = volume_issue_year[3].replace('(', '').replace(')', '')
    year = volume_issue_year[4].replace('(', '').replace(')', '')

    All_articles = current_soup.find("div", class_="main-right col-lg-9 col-md-9 col-sm-9 col-xs-9").findAll("div",class_="article-list article-list-en article-list-latest")
    Total_count = len(All_articles)
    print(f"Total number of articles:{Total_count}", "\n")
    article_index, article_check = 0, 0
    while article_index < len(All_articles):
        Article_link, Article_title = None, None
        try:
            Article_link = "https:"+All_articles[article_index].find('div',class_="article-list-title").find('a').get('href')
            Article_title= All_articles[article_index].find('div',class_="article-list-title").find('a').text.strip()
            html_content=All_articles[article_index].find('div',class_="article-list-time latest_info")
            doi = html_content.find("a").text.strip()
            font_tags = html_content.find_all('font')
            identifier = None
            for tag in font_tags:
                try:
                    text = tag.get_text()
                    match = re.search(r'\d{6}', text)
                    if match:
                        identifier = match.group()
                        break
                except Exception as e:
                    print(f'Error processing tag: {e}')

            a_tag = All_articles[article_index].find_all("font", class_="font3")[1]
            id = None
            if a_tag:
                try:
                    onclick_attr = a_tag.find('a')['onclick']
                    match = re.search(r"downloadpdf\('([^']+)'\)", onclick_attr)
                    if match:
                        id = match.group(1)
                except Exception as e:
                    print(f'Error processing tag: {e}')
            pdf_link=f"https://wulixb.iphy.ac.cn/en/article/exportPdf"
            payload={"id":id}

            check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
            if Check_duplicate.lower() == "true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", Article_title)

            else:
                session = requests.Session()
                retries = 0
                max_retries = 5
                download_successful = False

                while retries < max_retries and not download_successful:
                    response = session.post(pdf_link, data=payload, headers=headers)
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
                        {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "","Identifier": identifier,
                         "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": "", "Month": "", "Day": "","Year": year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title)

            if not Article_link in read_content:
                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                    write_file.write(Article_link + '\n')

            article_index, article_check = article_index + 1, 0

        except Exception as error:
            if article_check < 4:
                article_check += 1
            else:
                message = f"Error link - {Article_link} : {str(error)}"
                print("Download failed :", Article_title)
                error_list.append(message)
                article_index, article_check = article_index + 1, 0

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
        Error_message = "Error in the site:" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)