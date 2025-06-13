import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

month_conversion = {
    "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April",
    "May": "May", "Jun": "June", "Jul": "July", "Aug": "August",
    "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December"
}


current_date=None
current_time=None
ini_path=None
Total_count=None
Ref_value="170"


try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url_info_list = []
with open('urlDetails.txt', 'r') as file:
    for line in file:
        url, url_id = line.strip().split(',')
        url_info_list.append({"url": url, "url_id": url_id})


for url_info in url_info_list:
    try:
        url = url_info["url"]
        url_id = url_info["url_id"]

        attachment = None
        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path= os.path.join(os.getcwd(),"REF_170.ini")
        Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
        current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
        out_excel_file=common_function.output_excel_name(current_out)

        soup = get_soup(url)
        html_string=soup.find('div', class_='typography-body text-display1 font-content color-black f-6 ln-6').get_text(strip=True)

        pattern = r'Volume (\d+): Issue (\d+) \((\w+) (\d{4})\)'

        # Search for the pattern in the HTML string
        match = re.search(pattern, html_string)

        if match:
            volume = match.group(1)
            issue = match.group(2)
            month_abbr = match.group(3)
            year = match.group(4)

            # Convert abbreviated month to full month
            month = month_conversion.get(month_abbr, month_abbr)

            print(f"volume='{volume}', issue='{issue}', month='{month}', year='{year}'")
        else:
            print("Pattern not found in the string.")

        if url_id=="76469999":
            content_href = f"https://thejns.org/view/journals/j-neurosurg/{volume}/{issue}/j-neurosurg.{volume}.issue-{issue}.xml"
        elif url_id=="78877299":
            content_href=f"https://thejns.org/spine/view/journals/j-neurosurg-spine/{volume}/{issue}/j-neurosurg-spine.{volume}.issue-{issue}.xml"
        elif url_id == "79188999":
            content_href=f"https://thejns.org/pediatrics/view/journals/j-neurosurg-pediatr/{volume}/{issue}/j-neurosurg-pediatr.{volume}.issue-{issue}.xml"
        else:
            break

        content_soup=get_soup(content_href)
        content_archive = content_soup.find_all('div',class_="type-article leaf")
        length = len(content_archive)
        Total_count = len(content_archive)
        print(f"Total number of articles:{Total_count}", "\n")
        for element in content_archive:
            Article_link=None
            try:
                Article_link="https://thejns.org"+element.find("h2").find("a").get('href')

                article_soup = get_soup(Article_link)
                title=article_soup.find("h1",class_="typography-body title mb-3 text-headline font-content").get_text(strip=True)
                page_range=article_soup.find('dl',class_="pagerange c-List__items").find("dd",class_="pagerange inline c-List__item c-List__item--secondary text-metadata-value").find("span",class_="typography-body").get_text(strip=True)
                doi_text=article_soup.find("dd",class_="doi inline c-List__item c-List__item--secondary text-metadata-value").find("a",class_="c-Button--link").get('href')
                pattern = r'doi\.org/(10\.\d{4}/[\w.]+)'

                # Search for the pattern in the URL string
                match = re.search(pattern, doi_text)

                if match:
                    doi = match.group(1)
                else:
                    print("DOI not found in the URL.")

                pdf_link="https://thejns.org"+article_soup.find("div",class_="content-box box no-border no-header vertical-margin-bottom null").find("ul",class_="flat-list no-bullets").find("a").get('href')
                check_value, tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", title)
                else:
                    session = requests.Session()
                    retries = 0
                    max_retries = 5
                    download_successful = False

                    while retries < max_retries and not download_successful:
                        response = session.post(pdf_link,headers=headers)
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
                            {"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                             "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "", "Year": year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print("Original Article :", title)
            except Exception as error:
                message = f"Error link - {Article_link} : {str(error)}"
                error_list.append(message)
                print(error)
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
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass

    except Exception as error:
        Error_message = "Error in the site :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)

