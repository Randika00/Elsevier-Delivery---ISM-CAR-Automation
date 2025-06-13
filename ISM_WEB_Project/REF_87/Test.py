import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd
from googletrans import Translator

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
pdf_count=None
def translate_text(text, source_language='pt', target_language='en'):
    translator = Translator()
    translation = translator.translate(text, src=source_language, dest=target_language)
    return translation.text

def extract_info(text):
    volume_match = re.search(r'Volume:\s*(\d+)', text)
    volume = volume_match.group(1) if volume_match else None
    issue_match = re.search(r'Número:\s*(\d+)', text)
    issue = issue_match.group(1) if issue_match else ""
    year_match = re.search(r'Publicado:\s*(\d{4})', text)
    year = year_match.group(1) if year_match else None
    return volume,issue,year


def process_articles(current_issue_url,Check_duplicate):
    global pdf_count
    try:
        current_page = requests.get(current_issue_url, headers=headers)
        current_soup = BeautifulSoup(current_page.content, 'html.parser')
        text_element = current_soup.find("div", class_="collapse-content issueIndent").find("strong")
        if text_element:
            text = text_element.get_text(strip=True)
        else:
            text = None
        volume, issue, year = extract_info(text)
        li_elements = current_soup.find("ul", class_="articles").find_all('li', attrs={'data-date': True})
        for li_element in li_elements:
            try:
                full_title = li_element.find("h2")
                if full_title.find("span"):
                    span_ele=full_title.find("span")
                    span_ele.extract()
                title=full_title.text
                translated_title = translate_text(title)
                Article_url = "https://www.scielo.br" + li_element.find("ul", class_="links").find_all('a')[-2].get('href')
                if Article_url not in read_content:
                    pdf_link = "https://www.scielo.br" + li_element.find("ul", class_="links").find_all('a')[-1].get('href')
                    Article_page = requests.get(Article_url, headers=headers)
                    Article_soup = BeautifulSoup(Article_page.content, 'html.parser')
                    doi = Article_soup.find("a", class_="_doi").get_text(strip=True).rsplit("org/", 1)[-1]
                    if Check_duplicate.lower() == "true":
                        check_value = common_function.check_duplicate(doi, translated_title, url_id, volume, "")
                        if check_value:
                            message = f"{Article_url} - duplicate record with TPAID {{tpaid returned in response}}"
                            duplicate_list.append(message)
                            print("Duplicate Article :", translated_title)
                    else:
                        print("Original Article :", translated_title)
                        pdf_content = requests.get(pdf_link, headers=headers).content
                        output_file_name = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_file_name, 'wb') as file:
                            file.write(pdf_content)
                        print(f"Downloaded: {output_file_name}")
                        data.append({"Title": translated_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                     "Identifier": "", "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                     "Special Issue": "", "Page Range": "", "Month": "", "Day": "", "Year": year,
                                     "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": os.getlogin()})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_url}"
                        completed_list.append(scrape_message)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_url + '\n')
            except Exception as error:
                message = f"Error link - {Article_url} : {str(error)}"
                error_list.append(message)
                print(error)
    except Exception as error:
        message = f"Error processing articles for URL {url}: {str(error)}"
        error_list.append(message)
        print(error)

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

        ini_path = os.path.join(os.getcwd(), "REF_87.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        Ref_value = "87"
        print(url_id)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        if url_id!="78463099":
            current_issue_url = "https://www.scielo.br"+soup.find('tbody').find('td', class_='left').find_all('a')[-1].get("href")
            process_articles(current_issue_url,Check_duplicate)
        else:
            current_issue_urls = soup.find('tbody').find('td', class_='left').find_all('a')
            for current_issue_url in current_issue_urls:
                try:
                    current_issue_url1 = "https://www.scielo.br" + current_issue_url.get("href")
                    process_articles(current_issue_url1,Check_duplicate)
                except Exception as error:
                    message = f"Error processing articles for URL {url}: {str(error)}"
                    error_list.append(message)
                    print(error)

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