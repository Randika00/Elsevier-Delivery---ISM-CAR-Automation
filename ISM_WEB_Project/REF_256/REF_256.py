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

def extract_volume_issue_year(text):
    vol_issue_pattern = r"Vol\. (\d+)(?: No\. (\d+))?"
    year_pattern = r"\((\d{4})\)"
    vol_issue_match = re.search(vol_issue_pattern, text)
    volume = vol_issue_match.group(1) if vol_issue_match else ""
    issue = vol_issue_match.group(2) if vol_issue_match and vol_issue_match.group(2) else ""

    # Extract year
    year_match = re.search(year_pattern, text)
    year = year_match.group(1) if year_match else ""

    return volume, issue, year


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
            ini_path = os.path.join(os.getcwd(), "REF_256.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "256"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1

        currentSoup=get_soup(url)

        current_url=currentSoup.find("div",class_="col-12 col-sm issue-details").find('h2',class_="h_with_underline").find('a').get('href')
        soup=get_soup(current_url)

        en_link=soup.find('li',lang="en-US").find('a').get('href')
        en_soup = get_soup(en_link)

        combined_soup = str(soup) + str(en_soup)
        TOC_path, TOC_name = common_function.output_TOC_name(current_out)
        with open(TOC_path, 'w', encoding='utf-8') as html_file:
            html_file.write(str(combined_soup))
        print(f"TOC HTML file '{TOC_name}' has been saved successfully.")


        text = en_soup.find("div",class_="mt-0 current_issue_title h2 h_with_underline").get_text(strip=True)
        if not url_id=='933492618':
            volume, issue, year = extract_volume_issue_year(text)
            print(f"Volume: {volume}, Issue: {issue}, Year: {year}\n")
        else:
            match = re.search(r"No\. (\d+) \((\d+)\)", text)
            if match:
                volume = match.group(1)
                year = match.group(2)
                print(f"Volume: {volume}, Year: {year}")
            else:
                print("No match found")

        All_articles=en_soup.findAll("div",class_="col-12 col-sm article-summary-details pt-3 pt-sm-0")

        Total_count=len(All_articles)
        print(f"Total number of articles:{Total_count}","\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index+1
            Article_link, Article_title = None, None
            try:
                Article_title=All_articles[article_index].find("div",class_="title").find("a",class_="text-reset").text.strip()
                Article_link=All_articles[article_index].find("a",class_="text-reset").get("href")

                soup1=get_soup(Article_link)
                en_soup1_link=soup1.find('li',lang="en-US").find('a').get('href')
                en_soup1=get_soup(en_soup1_link)

                try:
                    DOI=en_soup1.find("section",class_="item doi").find("span",class_="value").find("a").text.strip().rsplit("org/",1)[-1]

                except:
                    print("Failed to find doi")
                    DOI="",""

                try:
                    pdf_link1=en_soup1.find('ul',class_="value galleys_links").find("li").find('a',class_="obj_galley_link pdf").get('href')
                    pdf_link1_soup=get_soup(pdf_link1)

                    pdf_link2=pdf_link1_soup.find("a",class_="download").get('href')
                except:
                    print("Failed to find pdf_link,Threre is no PDF")
                    pdf_link2=""

                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, volume, "")

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
                            pdf_content = requests.get(pdf_link2, headers=headers).content
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
                             "Special Issue": "", "Page Range": "", "Month": "", "Day": "",
                             "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})

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
            url_index, url_check = url_index + 1, 0

    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)