import re
import requests
from bs4 import BeautifulSoup
import os
import common_function
import pandas as pd
from datetime import datetime

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup


def get_ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

duplicate_list = []
error_list = []
completed_list = []
Total_count=None
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None

try:
    with open('urlDetails.txt','r',encoding='utf-8') as file:
        url_list=file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\" : " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        url, url_id = url_list[url_index].split(',')

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            ini_path = os.path.join(os.getcwd(), "REF_247.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "247"
        print(url_id)

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1

        soup=get_soup(url)
        current_iss_href="https://scholarlypublishingcollective.org"+soup.find("div",class_="view-current-issue").find("a").get('href')

        soup1=get_soup(current_iss_href)

        vol_iss_text=soup1.find("span",class_="volume issue").get_text(strip=True)
        match = re.search(r"Volume (\d+)(?:, Issue ([\d\-]+))?", vol_iss_text)
        if match:
            volume = match.group(1)if match.group(1) is not None else ""
            issue = match.group(2) if match.group(2) is not None else ""
            print(f"Volume: {volume}, Issue: {issue}")
        else:
            print("No match found")
        year_month_text = soup1.find("div", class_="ii-pub-date").get_text(strip=True)
        match = re.search(r"([A-Za-z]+) (\d{4})", year_month_text)

        if match:
            month = match.group(1)
            year = match.group(2)
            print(f"Month: {month}, Year: {year}")
        else:
            print("No match found")

        All_articles=soup1.findAll("div",class_="al-article-items")

        Total_count=len(All_articles)
        print(f"Total number of articles:{Total_count}","\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index+1
            Article_link, Article_title = None, None
            try:
                Article_title=All_articles[article_index].find("h5",class_="customLink item-title").find("a").text.strip()
                Article_link="https://scholarlypublishingcollective.org"+All_articles[article_index].find("h5",class_="customLink item-title").find("a").get("href")

                soup2=get_soup(Article_link)

                page_range_text=soup2.find("div",class_="ww-citation-primary").get_text(strip=True)
                match = re.search(r": (\d+[\–\-]\d+)", page_range_text)

                if match:
                    page_range = match.group(1)
                    print(f"Page Range: {page_range}")
                else:
                    # If no page range is found, return an empty string
                    page_range = ""
                    print(f"Page Range: {page_range}")

                try:
                    DOI=soup2.find("div",class_="citation-doi").find("a").text.strip().rsplit("org/",1)[-1]

                except:
                    print("Failed to find doi")
                    DOI=""

                pdf_link="https://scholarlypublishingcollective.org"+soup2.find('a',class_="al-link pdf openInAnotherWindow stats-item-pdf-download js-download-file-gtm-datalayer-event article-pdfLink").get('href')


                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, volume, issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count)+" article is duplicated article" +"\n"+"Article title:", Article_title,"\n")

                else:
                    print("Wait until the PDF is downloaded")
                    output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                    retry_count = 0
                    max_retries = 10
                    success = False

                    while retry_count < max_retries and not success:
                        try:
                            pdf_content = requests.get(pdf_link, headers=headers).content
                            with open(output_fileName, 'wb') as file:
                                file.write(pdf_content)
                            success = True
                            print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")
                        except Exception as e:
                            retry_count += 1
                            print(f"Failed to download PDF on attempt {retry_count}. Error: {e}")
                            if retry_count == max_retries:
                                print("Maximum retry attempts reached, download failed.")
                    if success:
                        data.append(
                            {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                             "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "",
                             "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})

                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print(get_ordinal_suffix(Article_count)+" article is original article" +"\n"+"Article title:", Article_title,"\n")

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"{Article_link} : {str(error)}"
                    print(get_ordinal_suffix(Article_count)+" article could not be downloaded due to an error"+"\n"+"Article title:", Article_title,"\n")
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0
        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)),str(len(error_list)))
        except Exception as error:
            message=str(error)
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
            print(Error_message,"\n")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)

            url_index, url_check = url_index + 1, 0