import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
Total_count=None

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


url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        url, url_id = url_list[url_index].split(',')

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "REF_279.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "279"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1
        url_value=url.split('/')[-3]

        soup=get_soup(url)

        current_issue =soup.find("div", class_="pkp_navigation_primary_row").findNext("ul", class_="pkp_navigation_primary pkp_nav_list").find("li").find("a").get('href')
        current_soup = get_soup(current_issue)

        text = current_soup.find("div",class_="page page_issue").find("h1").get_text(strip=True)

        pattern = r"Vol (\d+) No (\d+) \((\d{4})\)"

        match = re.search(pattern, text)

        if match:
            volume = match.group(1)
            issue = match.group(2)
            year = match.group(3)

            print(f"Volume: {volume}")
            print(f"Issue: {issue}")
            print(f"Year: {year}")
        else:
            print("No match found")

        All_articles = current_soup.find("div", class_="sections").findAll("div", class_="obj_article_summary")
        Total_count = len(All_articles)
        print(f"Total number of articles:{Total_count}", "\n")
        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link, Article_title = None, None
            try:
                Article_link = All_articles[article_index].find('h3',class_='title').find('a').get('href')
                Article_title = All_articles[article_index].find('h3',class_='title').find('a').text.strip()
                page_range=All_articles[article_index].find('div',class_='meta').find("div",class_="pages").text.strip()

                article_soup = get_soup(Article_link)

                doi_text = article_soup.find("div",class_="main_entry").find("section",class_="item doi").find("span",class_="value").text.strip()

                pattern = r"https://doi\.org/(10\.\d{4,9}/[-._;()/:A-Z0-9]+)"

                match = re.search(pattern, doi_text, re.IGNORECASE)

                if match:
                    doi = match.group(1)
                    print(f"Extracted DOI: {doi}")
                else:
                    print("No match found")

                pdf_link_tag = article_soup.find('a', class_='obj_galley_link pdf')
                pdf_page_link = pdf_link_tag['href'] if pdf_link_tag else None

                pdf_soup = get_soup(pdf_page_link)

                pdf_link=pdf_soup.find("header",class_="header_view").find("a",class_="download").get('href')

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
                        response = session.get(pdf_link,headers=headers)
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
                            {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                             "Identifier":"",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": "", "Day": "", "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print("Original Article :", Article_title)

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
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)
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
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)

            url_index, url_check = url_index + 1, 0