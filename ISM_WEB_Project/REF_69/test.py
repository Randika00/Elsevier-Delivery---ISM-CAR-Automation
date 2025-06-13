import requests
from bs4 import BeautifulSoup
import os
import re
import captcha_main
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

Total_count = None
url_info_list = []
with open('urlDetails.txt', 'r') as file:
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

for url_info in url_info_list:
    try:
        url = url_info["url"]
        url_id = url_info["url_id"]
        pdf_count = 1
        duplicate_list = []
        error_list = []
        completed_list = []
        data = []

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "Info.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        Ref_value = "69"
        print(url_id)

        page = captcha_main.captcha_main(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        volume_issue_span = soup.find('span', class_='volume issue')
        if volume_issue_span:
            volume_issue_text = volume_issue_span.text.strip()
            volume, issue = volume_issue_text.split(', ')
            volume = volume.split()[1]
            issue = issue.split()[1]
        pub_date_div = soup.find('div', class_='ii-pub-date')
        if pub_date_div:
            date_text = pub_date_div.text.strip()
            month, year = date_text.split()
        articles = soup.find_all("div", class_="al-article-items")
        Total_count = len(articles)
        print(f"Total number of articles: {Total_count}", "\n")
        for article in articles:
            Article_link = None
            try:
                title_element = article.find('a')
                if title_element:
                    title = title_element.text.strip()
                    Article_link = title_element.get("href")
                    doi_element = article.find("div", class_="ww-citation-primary").find('a').text
                    if doi_element:
                        doi = doi_element.split("https://doi.org/")[-1]
                    citation_text = article.find('div', class_='ww-citation-primary').text.strip()
                    page_range = citation_text.split()[-2].rstrip('.')
                    article_url = article.find("div", class_="resource-links-info").find("a", class_="al-link pdf openInAnotherWindow stats-item-pdf-download js-download-file-gtm-datalayer-event article-pdfLink").get("href")
                    pdf_link = "https://onepetro.org" + article_url
                    check_value, tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print("Duplicate Article :", title)
                    else:
                        print("Original Article :", title)
                        pdf_content = requests.get(pdf_link, headers=headers).content
                        output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_fileName, 'wb') as file:
                            file.write(pdf_content)
                        print(f"Downloaded: {output_fileName}")
                        data.append(
                            {"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "", "Year": year,
                             "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_link + '\n')
            except Exception as error:
                message = f"Error link - {Article_link} : {str(error)}"
                error_list.append(message)
                print(error)

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)), str(len(error_list)))
        except Exception as error:
            message = str(error)
            error_list.append(message)
        if str(Email_Sent).lower() == "true":
            attachment_path = out_excel_file
            if os.path.isfile(attachment_path):
                attachment = attachment_path
            else:
                attachment = None
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
    except Exception as error:
        Error_message = "Error in the site :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list, completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)

        print("Error details file saved to:", error_file_path)
