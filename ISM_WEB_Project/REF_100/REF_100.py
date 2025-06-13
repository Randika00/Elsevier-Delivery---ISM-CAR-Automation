import requests
from bs4 import BeautifulSoup
import os
import re
import captcha_main
import common_function
from datetime import datetime
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
}

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    current_issue_link = "https://research.aota.org" + soup.find("div", class_="view-current-issue").find("a").get("href")
    return soup

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

Total_count=None
attachment=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
current_datetime = datetime.now()
current_date = str(current_datetime.date())
current_time = current_datetime.strftime("%H:%M:%S")

ini_path= os.path.join(os.getcwd(),"REF_100.ini")
Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
duplicate_list = []
error_list = []
completed_list=[]
data = []
pdf_count = 1
Ref_value="100"
url_id='76209399'

current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
out_excel_file=common_function.output_excel_name(current_out)

url = "https://research.aota.org/ajot"
try:
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        current_issue_link = "https://research.aota.org" + soup.find("div", class_="view-current-issue").find("a").get("href")
    except:
        print("Attempting to solve CAPTCHA.")
        response = captcha_main.captcha_main(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    finally:
        current_issue_link="https://research.aota.org"+soup.find("div",class_="view-current-issue").find("a").get("href")
        try:
            response2= requests.get(current_issue_link, headers=headers)
            current_soup= BeautifulSoup(response2.content, 'html.parser')
            volume_issue_span = current_soup.find('span', class_='volume issue')
            if volume_issue_span is None:
                raise ValueError("CAPTCHA occurred, waiting until solved.")
        except Exception as e:
            print("Attempting to solve 2nd CAPTCHA.")
            response2=captcha_main.captcha_main(current_issue_link)
            current_soup= BeautifulSoup(response2.content, 'html.parser')
        finally:
            volume_issue_span = current_soup.find('span', class_='volume issue')
            volume_issue_text = volume_issue_span.get_text()
            match = re.search(r'Volume (\d+), Issue (\d+)', volume_issue_text)
            if match:
                volume = match.group(1)
                issue = match.group(2)
            pub_date_div = current_soup.find('div', class_='ii-pub-date')
            if pub_date_div:
                date_text = pub_date_div.get_text().strip()
                months = date_text.split('/')[0].strip()
                year = date_text.split()[-1]
            All_articles=current_soup.find_all("div",class_="al-article-items")
            All_articles_count = len(current_soup.find_all("div", class_="al-article-items"))
            Total_count = len(All_articles)
            print(f"Total number of articles:{Total_count}", "\n")
            i, j = 0, 0
            while i < len(All_articles):
                Article_link = None
                Article_title=None
                try:
                    Article_link="https://research.aota.org"+All_articles[i].find("h5",class_="customLink item-title").find("a").get("href")
                    Article_title=All_articles[i].find("h5",class_="customLink item-title").find("a").get_text(strip=True)
                    try:
                        response3= requests.get(Article_link, headers=headers)
                        article_soup= BeautifulSoup(response3.content, 'html.parser')
                        citation_div = article_soup.find('div', class_='ww-citation-primary')
                        if citation_div is None:
                            raise ValueError("CAPTCHA occurred, waiting until solved.")
                    except:
                        print("Attempting to solve 3rd CAPTCHA.")
                        response3 = captcha_main.captcha_main(Article_link)
                        article_soup=BeautifulSoup(response3.content, 'html.parser')
                    finally:
                        citation_div = article_soup.find('div', class_='ww-citation-primary')
                        if citation_div:
                            citation_text = citation_div.get_text().strip()
                            match = re.search(r'(\d{10})\.$', citation_text)
                            if match:
                                identifier = match.group(1)
                            else:
                                print("Identifier not found.")
                        doi_div = article_soup.find('div', class_='citation-doi')
                        if doi_div:
                            doi_link = doi_div.find('a').get('href')
                            doi = doi_link.rsplit('org/',1)[-1]
                        pdf_link="https://research.aota.org"+article_soup.find("li",class_="toolbar-item item-with-dropdown item-pdf").find("a",class_="al-link pdf openInAnotherWindow stats-item-pdf-download js-download-file-gtm-datalayer-event article-pdfLink").get("href")
                        check_value,tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
                        if Check_duplicate.lower() == "true" and check_value:
                            message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                            duplicate_list.append(message)
                            print("Duplicate Article :", Article_title)
                        else:
                            print("Original Article :", Article_title)
                            output_file_path = os.path.join(current_out, f"{pdf_count}.pdf")
                            pdf_response = requests.get(pdf_link, headers=headers)
                            pdf_content = pdf_response.content

                            soup_test= str(BeautifulSoup(pdf_content, 'html.parser'))

                            if 'explanation-message' in soup_test:
                                print("Attempting to solve PDF CAPTCHA.")
                                response = captcha_main.captcha_main(pdf_link)
                                pdf_content = response.content
                                output_file_path = os.path.join(current_out, f"{pdf_count}.pdf")
                                if response.status_code == 200:
                                    with open(output_file_path, 'wb') as file:
                                        file.write(pdf_content)
                                    print(f"PDF downloaded successfully: {output_file_path}")
                                else:
                                    print(f"Failed to download PDF. Status code: {response.status_code}")
                            else:
                                # No CAPTCHA detected, save the PDF content
                                with open(output_file_path, 'wb') as file:
                                    file.write(pdf_content)
                                print(f"PDF downloaded successfully: {output_file_path}")


                            data.append(
                                {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "","Identifier": identifier,
                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "","Special Issue": "", "Page Range": "", "Month": months, "Day": "","Year": year,
                                 "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                            df = pd.DataFrame(data)
                            df.to_excel(out_excel_file, index=False)
                            pdf_count += 1
                            scrape_message = f"{Article_link}"
                            completed_list.append(scrape_message)
                            with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                write_file.write(Article_link + '\n')
                    i, j = i + 1, 0
                except Exception as error:
                    if j < 0:
                        j+= 1
                    else:
                        message = f"Error link - {Article_link} : {str(error)}"
                        print("Download failed :", Article_title)
                        error_list.append(message)
                        i, j = i + 1, 0
            try:
                common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                                str(len(duplicate_list)), str(len(error_list)))
            except Exception as error:
                message = str(error)
                error_list.append(message)
            if str(Email_Sent).lower() == "true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)
            sts_file_path=os.path.join(current_out,'Completed.sts')
            with open(sts_file_path,'w') as sts_file:
                pass
except Exception as error:
    Error_message = "Error in the site :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)


