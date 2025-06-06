import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
import os
import time
import common_function

source_id = "951527209"

duplicate_list = []
error_list = []
completed_list = []
attachment = None
current_date = None
current_time = None
Ref_value = None
time_prefix = None
today_date = None
ini_path = None

def fetch_url(url, headers, retries=5, backoff_factor=0.3):
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in {backoff_factor * (2 ** i)} seconds...")
            time.sleep(backoff_factor * (2 ** i))
    raise requests.exceptions.RequestException(f"Failed to fetch URL {url} after {retries} retries.")

try:
    try:
        with open('urlDetails.txt', 'r', encoding='utf-8') as file:
            url_details = file.readlines()
    except Exception as error:
        Error_message = "Error in the urlDetails.txt file :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                             ini_path, attachment, current_date, current_time, Ref_value)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    try:
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')
    except FileNotFoundError:
        with open('completed.txt', 'w', encoding='utf-8'):
            with open('completed.txt', 'r', encoding='utf-8') as read_file:
                read_content = read_file.read().split('\n')

    for line in url_details:
        try:
            url, source_id = line.strip().split(",")
            base_url = "https://sjdlyj.ecnu.edu.cn/EN/"
            toc_url = "https://sjdlyj.ecnu.edu.cn/EN/1004-9479/current.shtml"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_215.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "215"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = fetch_url(url, headers)
            current_link = BeautifulSoup(response.content, "html.parser").find("ul", class_="nav navbar-nav").findAll("li")[5].find("a").get("href")

            response = fetch_url(current_link, headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="content_nr").findAll("div", class_="noselectrow")

                Total_count = len(div_element)
                print(f"Total number of articles:{Total_count}", "\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title = single_element.find("a", class_="txt_biaoti").text.strip()

                        article_link = single_element.find("a", class_="txt_biaoti").get('href')

                        pages_info = single_element.find("span", class_="abs_njq")

                        match = re.search(r'(\d+-\d+)', pages_info.text)
                        page_range = ""
                        if match:
                            page_range = match.group(1)

                        doi_tag = single_element.find("span", class_="abs_njq")

                        doi_link = pages_info.find("a", href=True)
                        doi = ""
                        if doi_link:
                            doi = doi_link['href'].replace("https://doi.org/", "") if doi_link else ""

                        month_year_info = soup.find("span", class_="date")
                        if month_year_info:
                            date_text = month_year_info.text.strip()
                            date_match = re.search(r'(\d+)\s(\w+)\s(\d{4})', date_text)
                            month, day, year = "", "", ""
                            if date_match:
                                day = date_match.group(1)
                                month = date_match.group(2)
                                year = date_match.group(3)

                            volume_issue_match = re.search(r'Volume\s(\d+)\sIssue\s(\d+)', date_text)
                            volume, issue = "", ""
                            if volume_issue_match:
                                volume = volume_issue_match.group(1)
                                issue = volume_issue_match.group(2)

                            onclick_attr = single_element.find("a", string="PDF")
                            if onclick_attr:
                                onclick_text = str(onclick_attr)
                                id_match = re.search(r"lsdy1\('PDF','(\d+)'", onclick_attr['onclick'])
                                pdf_id = ""
                                if id_match:
                                    pdf_id = id_match.group(1)

                                    base_pdf_url = "https://sjdlyj.ecnu.edu.cn/EN/article/downloadArticleFile.do?attachType=PDF&id="

                                    pdf_link = base_pdf_url + str(pdf_id)

                                    check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                    if Check_duplicate.lower() == "true" and check_value:
                                        message = f"{article_link} - duplicate record with TPAID : {tpa_id}"
                                        duplicate_list.append(message)
                                        print("Duplicate Article :", article_title)

                                    else:
                                        pdf_response = fetch_url(pdf_link, headers)
                                        pdf_content = pdf_response.content
                                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                        with open(output_fimeName, 'wb') as file:
                                            file.write(pdf_content)
                                        data.append(
                                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                                             "Identifier": "",
                                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                             "Special Issue": "", "Page Range": page_range, "Month": month, "Day": day,
                                             "Year": year,
                                             "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                             "user_id": user_id, "TOC File Name": f"{source_id}_TOC.html"})
                                        df = pd.DataFrame(data)
                                        df.to_excel(out_excel_file, index=False)
                                        pdf_count += 1
                                        scrape_message = f"{article_link}"
                                        completed_list.append(scrape_message)
                                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                            write_file.write(article_link + '\n')
                                        print("Original Article :", article_link)

                    except Exception as error:
                        message = f"Error link - {article_title} : {str(error)}"
                        print(f"{article_title} : {str(error)}")
                        error_list.append(message)

                try:
                    try:
                        response_en = requests.get(toc_url, headers=headers, timeout=30)
                        response_en.raise_for_status()
                        soup_en = BeautifulSoup(response_en.text, 'html.parser')

                        english_heading = "<h1>Table of Contents - English Version</h1>\n"
                        english_content = soup_en.prettify()

                    except Exception as e:
                        error_message = f"Error processing English version of URL {toc_url}: {str(e)}"
                        error_list.append(error_message)
                        print(error_message)
                        english_heading = "<h1>Error loading English version</h1>\n"
                        english_content = f"<p>{error_message}</p>\n"

                    try:
                        url_cn = toc_url.replace('/EN', '/CN')

                        response_cn = requests.get(url_cn, headers=headers, timeout=30)
                        response_cn.raise_for_status()
                        soup_cn = BeautifulSoup(response_cn.text, 'html.parser')

                        chinese_heading = "<h1>Table of Contents - Chinese Version</h1>\n"
                        chinese_content = soup_cn.prettify()

                    except Exception as e:
                        error_message = f"Error processing Chinese version of URL {toc_url}: {str(e)}"
                        error_list.append(error_message)
                        print(error_message)
                        chinese_heading = "<h1>Error loading Chinese version</h1>\n"
                        chinese_content = f"<p>{error_message}</p>\n"

                    combined_content = f"{english_heading}{english_content}<hr>{chinese_heading}{chinese_content}"

                    # Save combined content to HTML file
                    output_file = os.path.join(current_out, f"{source_id}_TOC.html")
                    with open(output_file, 'w', encoding='utf-8') as file:
                        file.write(combined_content)

                    print(f"Combined file saved: {output_file}")

                except Exception as e:
                    print(f"Error in creating the TOC file: {e}")
                    error_list.append(f"Error in creating the TOC file: {e}")

                try:
                    common_function.sendCountAsPost(source_id, Ref_value, str(Total_count), str(len(completed_list)),
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
                        common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
                                                             len(completed_list), ini_path, attachment, current_date,
                                                             current_time, Ref_value)
                except Exception as error:
                    message = f"Failed to send email : {str(error)}"
                    error_list.append(message)

                sts_file_path = os.path.join(current_out, 'Completed.sts')
                with open(sts_file_path, 'w') as sts_file:
                    pass

        except Exception as e:
            Error_message = "Error in the site :" + str(e)
            print(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)

except Exception as error:
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
