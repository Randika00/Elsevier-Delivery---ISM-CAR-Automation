import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import zipfile
import os
import shutil
import glob
import pandas as pd
import common_function

def format_date(date_str):
    date_object = datetime.strptime(date_str, '%d %B %Y')
    year = date_object.year
    month = date_object.strftime('%B')
    day = date_object.day
    return year, month, day


def get_xml(file_url,current_out,pdf_count):
    local_filename = 'downloaded_file.zip'
    response = requests.get(file_url, stream=True)
    with open(local_filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)

    zip_file_path = 'downloaded_file.zip'
    extract_folder = 'extracted_folder'
    output_fimeName=os.path.join(current_out,f"{pdf_count}.xml")

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    xml_files = glob.glob(os.path.join(extract_folder, '**', 'fulltext.xml'), recursive=True)
    if not xml_files:
        print('Error: Could not find fulltext.xml within the extracted folder.')
    else:
        xml_file_path = xml_files[0]
        try:
            with open(xml_file_path, 'rb') as xml_file, open(output_fimeName, 'wb') as out_file:
                out_file.write(xml_file.read())
            print(f'Content of fulltext.xml saved as {output_fimeName}')
        except Exception as e:
            print(e)
    os.remove(local_filename)
    shutil.rmtree(extract_folder)
def process_articles(all_articles, month, year):
    global pdf_count,current_out
    for all_article in all_articles:
        Article_link = None
        try:
            title = all_article.find('h5', class_='title').text.strip()
            Article_link="https://journals.aps.org"+all_article.find('h5', class_='title').find("a").get("href")
            doi = str(all_article.find('a').get('href')).rsplit('abstract/', 1)[-1]
            url = 'http://harvest.aps.org/bagit/articles/' + doi + '/apsxml'
            article_url = 'https://journals.aps.org' + all_article.find('h5', class_='title').find('a').get('href')
            identifier = doi[-6:]
            check_value,tpa_id = common_function.check_duplicate(doi, title, url_id, volume_number, issue_number)
            if Check_duplicate.lower()=="true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :",title)
            else:
                print("Original Article :",title)
                get_xml(url,current_out,pdf_count)
                data.append({"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": identifier, "Volume": volume_number,
                             "Issue": issue_number, "Supplement": "", "Part": "", "Special Issue": "", "Page Range": "", "Month": month, "Day": "", "Year": year,
                             "URL": article_url, "SOURCE File Name": f"{pdf_count}.xml", "user_id": user_id})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                pdf_count += 1
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
            if not Article_link in read_content:
                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                    write_file.write(Article_link + '\n')
        except Exception as error:
            message = f"Error link - {Article_link} : {str(error)}"
            error_list.append(message)

Total_count=None
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
current_out=None
url_info_list = []
with open('APS_links.txt', 'r') as file:
    for line in file:
        url, url_id = line.strip().split(',')
        url_info_list.append({"url": url, "url_id": url_id})

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

class Issues_link_soup:
    pass

for url_info in url_info_list:
    try:
        url = url_info["url"]
        url_id = url_info["url_id"]

        date = []
        url_list = []
        data = []
        duplicate_list = []
        completed_list = []
        error_list = []
        count = 1
        pdf_count = 1
        Ref_value = "2"

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "Info.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        Ref_value ="2"

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        panel = soup.findAll('div', class_='panel')[1].find('div', class_='volume-issue-list')
        urls = 'https://journals.aps.org' + panel.find('a').get('href')
        issues_page = requests.get(urls)
        issues_soup = BeautifulSoup(issues_page.content, 'html.parser')
        all_issue = issues_soup.findAll('div', class_='panel')[1].find('div', class_='volume-issue-list')
        if all_issue.find('ul'):
            volume = re.sub(r'[^0-9]+', '', all_issue.find('h4').find('a').text.strip())
            all_link = all_issue.find('ul').find_all('li')[-1]
            new_link = 'https://journals.aps.org' + all_link.find('a').get('href')
            issues_link = requests.get(new_link)
            issues_link_soup = BeautifulSoup(issues_link.content, 'html.parser')
            volume_panel = issues_link_soup.find('div', class_='panel').find('h2').text.strip()
            match = re.search(r"Volume (\d+), Issue (\d+)", volume_panel)
            if match:
                volume_number = match.group(1)
                issue_number = match.group(2)
            else:
                print("Pattern not found")
            if url_id not in {"78809999", "637565102", "644500202", "926471598", "933052813","78048999", "297249199"}:
                date_str = issues_link_soup.find('div', class_='panel').find('h5').text.strip()
                date_parts = date_str.split()
                if len(date_parts) == 2:
                    month, year = date_parts
                    print(f"Month: {month}, Year: {year}")
                else:
                    date, month, year = date_parts
                    print(f"Date: {date}, Month: {month}, Year: {year}")
                all_sections = issues_link_soup.findAll('section', class_='open')
                article_count=issues_link_soup.findAll('div',class_='article panel article-result')
                Total_count = len(article_count)
                print(f"Total number of articles:{Total_count}", "\n")
                for section in all_sections:
                    try:
                        all_articles = section.findAll('div',class_='article panel article-result')
                        process_articles(all_articles, month, year)
                    except Exception as all_sections_error:
                        print(all_sections_error)
            elif url_id in {"78048999", "297249199","78809999"}:
                date_str = issues_link_soup.find('div', class_='panel').find('h5').text.strip()
                month_year_parts = date_str.split()
                month = ' '.join(month_year_parts[:-1])
                year = month_year_parts[-1]
                print("Month:", month)
                print("Year:", year)
                all_articles = issues_link_soup.find_all('div',class_='article panel article-result')
                Total_count = len(all_articles)
                print(f"Total number of articles:{Total_count}", "\n")
                process_articles(all_articles, month, year)
            else:
                date_str = issues_link_soup.find('div', class_='panel').find('h5').text.strip()
                month_year_parts = date_str.split()
                month = ' '.join(month_year_parts[:-1])
                year = month_year_parts[-1]
                print("Month:", month)
                print("Year:", year)
                all_sections = issues_link_soup.find('div', class_='search-results').findAll()
                count = 0
                new_elements = []
                for element in all_sections:
                    if element.name == 'h2':
                        count += 1
                    if count >= 2 and element.name == 'div':new_elements.append(element)
                new_elements_html = ''.join(str(e) for e in new_elements)
                new_elements_soup = BeautifulSoup(new_elements_html, 'html.parser')
                all_articles = new_elements_soup.find_all('div',class_='article panel article-result')
                Total_count = len(all_articles)
                print(f"Total number of articles:{Total_count}", "\n")
                process_articles(all_articles, month, year)

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)),str(len(error_list)))
        except Exception as error:
            message=str(error)
            error_list.append(message)

        try:
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
    except Exception as error:
        Error_message = "Error in the site :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)




