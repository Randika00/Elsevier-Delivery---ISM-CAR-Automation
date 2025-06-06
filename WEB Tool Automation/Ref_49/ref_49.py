import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd

def get_soup(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

duplicate_list = []
error_list = []
completed_list = []
attachment = None
url_id = None
current_date = None
current_time = None
Ref_value = None
ini_path = None

try:
    with open('urlDetails.txt', 'r', encoding='utf-8') as file:
        url_list = file.read().split('\n')
except Exception as error:
    Error_message = "Error in the urls text file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

for i, url_url_id in enumerate(url_list):
    try:
        url, url_id = url_url_id.split(',')
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "Ref_49.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1
        Ref_value = "49"
        url_value = url.split('/')[-2]

        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        print(url_id)

        current_soup = get_soup(url)

        All_articles = current_soup.find_all('div', class_='article-list-right')

        articles_with_checkboxes_count = 0
        for div in All_articles:
            try:
                checkbox_input = div.find_previous_sibling('div', class_='article-list-left').find('input',
                                                                                                   type='checkbox')
                if checkbox_input:
                    articles_with_checkboxes_count += 1
            except AttributeError:
                pass

        status = 0
        # print("Number of articles : ", articles_with_checkboxes_count)
        Total_count = len(All_articles)
        # print(f"Total number of articles:{Total_count}", "\n")

        for div in All_articles:
            article_link, article_title = None, None
            try:

                id_value_checkbox = div.find_previous_sibling('div', class_='article-list-left')
                checkbox_input = id_value_checkbox.find('input', type='checkbox')
                id_value = id_value_checkbox.input['value']
                pdf_url = f'https://www.lcgdbzz.org/article/exportPdf?id={id_value}&language=en'

                if checkbox_input:
                    try:
                        article_title = div.find('div', class_='article-list-title').text.strip()
                        relative_url = div.find('div', class_='article-list-title').find('a').get('href')
                        article_link = "https://www.lcgdbzz.org" + relative_url
                        doi = div.find('a', class_='mainColor').text.strip()
                        page_range = \
                            div.find('div', class_='article-list-time').find('font').get_text().split(':')[
                                1].strip().rstrip('.')
                        id_value = div.find('div', class_='article-list-title')

                        metadata_div = current_soup.find('div', class_='nq')
                        metadata_text = metadata_div.text.strip()

                        metadata_parts = metadata_text.split()
                        volume, issue, month, year = "", "", "", ""
                        if len(metadata_parts) >= 5:
                            volume = metadata_parts[0].split('.')[1]
                            issue = metadata_parts[1].split('.')[1]
                            month = metadata_parts[5]
                            year = metadata_parts[6]

                        month_names = {
                            "Jan.": "January", "Feb.": "February", "Mar.": "March",
                            "Apr.": "April", "May": "May", "Jun.": "June",
                            "Jul.": "July", "Aug.": "August", "Sep.": "September",
                            "Oct.": "October", "Nov.": "November", "Dec.": "December"
                        }

                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, url_id, volume, issue)
                        if Check_duplicate.lower() == "true" and check_value:
                            message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                            duplicate_list.append(message)
                            print("Duplicate Article :", article_title)

                        else:
                            pdf_content = requests.get(pdf_url, headers=headers).content
                            output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                            with open(output_fimeName, 'wb') as file:
                                file.write(pdf_content)
                            data.append(
                                {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                 "ItemID": "",
                                 "Identifier": "",
                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                 "Special Issue": "", "Page Range": page_range,
                                 "Month": month_names.get(month, month), "Day": "",
                                 "Year": year,
                                 "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                 "user_id": user_id})
                            df = pd.DataFrame(data)
                            df.to_excel(out_excel_file, index=False)
                            pdf_count += 1
                            scrape_message = f"{article_link}"
                            completed_list.append(scrape_message)
                            with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                write_file.write(article_link + '\n')
                            print("Original Article :", article_link)

                    except Exception as e:
                        message = f"Error link - {article_title} : {str(e)}"
                        print(f"{article_title} : {str(e)}")
                        error_list.append(message)
                        All_articles.append(div)
                else:
                    status += 1
                    print(
                        f"The total number of {articles_with_checkboxes_count} downloads {status} PDFs have downloaded.")
            except:
                # ignore the irrelevant articles
                pass

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                            str(len(duplicate_list)),
                                            str(len(error_list)))
        except Exception as error:
            message = f"Failed to send post request : {str(error)}"
            error_list.append(message)

        try:
            if str(Email_Sent).lower() == "true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list), ini_path, attachment, current_date, current_time,
                                                     Ref_value)
        except Exception as error:
            message = f"Failed to send email : {str(error)}"
            error_list.append(message)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass

    except Exception as error:
        Error_message = "Error in the site :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                             ini_path, attachment, current_date, current_time, Ref_value)

