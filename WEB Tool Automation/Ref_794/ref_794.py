import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import common_function

source_id = "77880799"

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

def get_response_with_retry(url, headers, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    response = session.get(url, headers=headers, timeout=30)
    return response

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
            base_url = "https://www.hplpb.com.cn"
            toc_url = "https://www.hplpb.com.cn/en/article/current"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_794.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "794"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            link = BeautifulSoup(response.content, "html.parser").find("ul", class_="nav-inner clearfix container").find("li", attrs={"type": "current_en"}).find("a").get("href")
            current_link = base_url + link

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", id="lan", class_="articleListBox active base-catalog").findAll("div", class_="article-list")
                Total_count = len(div_element)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("div", class_="article-list-title")
                        if article_title_div:
                            article_title = article_title_div.find("a").text.strip()
                            article_link = article_title_div.find("a").get('href')

                            year_volume_article_doi_text = single_element.find("div", class_="article-list-time")
                            year, volume, article_number, doi = "", "", "", ""
                            if year_volume_article_doi_text:
                                year_volume_article = year_volume_article_doi_text.find("font").text.strip()
                                # match = re.search(r"(\d{4}),\s+(\d+):\s+(\d+)", year_volume_article)

                                match = re.search(r"(\d{4}),\s+(\d+):\s+([\d-]+)", year_volume_article)
                                if match:
                                    year = match.group(1) if year_volume_article else ""
                                    volume = match.group(2) if year_volume_article else ""
                                    article_number = match.group(3) if year_volume_article else ""

                                    doi_element = year_volume_article_doi_text.find("a", class_="mainColor")
                                    if doi_element:
                                        doi = doi_element.get('href').replace("https://dx.doi.org/", "")
                                    else:
                                        doi = ""

                                onclick_attr = single_element.find("div", class_="article-list-zy clear").find_all("a")
                                filtered_links = filter(lambda link: link.get("onclick"), onclick_attr)

                                id_values = list(map(lambda link: re.search(r"downloadpdf\('(.+?)'\)", link.get("onclick")).group(1), filtered_links))

                                id_values_string = " ".join(id_values)

                                pdf_link = f"https://www.hplpb.com.cn/article/exportPdf?id={id_values_string}&language=en"
                                xml_link = f"https://www.hplpb.com.cn/article/exportXML?ids={id_values_string}&downType=XML&language=en"

                                article_response = get_response_with_retry(article_link, headers)
                                if article_response.status_code == 200:
                                    article_soup = BeautifulSoup(article_response.content, 'html.parser')

                                    issue_tag = article_soup.find("div", class_="wrapper")
                                    issue = ""
                                    if issue_tag:
                                        issue_text = issue_tag.find("span", class_="issue")
                                        if issue_text:
                                            issue = re.search(r'\d+', issue_text.text).group(0) if issue_text else ""

                                    month_tag = article_soup.find("div", class_="wrapper")
                                    month = ""
                                    if month_tag:
                                        month_text = month_tag.find("div", class_="ii-pub-date")
                                        if month_text:
                                            month_abbr_match = re.search(r'([A-Za-z]+)', month_text.text.strip())
                                            if month_abbr_match:
                                                month_abbr = month_abbr_match.group(1) if month_text else ""
                                                try:
                                                    month = datetime.strptime(month_abbr, "%b").strftime("%B")
                                                except ValueError:
                                                    print(f"Error: Invalid month abbreviation '{month_abbr}'")

                                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                        if Check_duplicate.lower() == "true" and check_value:
                                            message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                            duplicate_list.append(message)
                                            print("Duplicate Article:", article_title)

                                        else:
                                            pdf_content = get_response_with_retry(pdf_link, headers=headers).content
                                            output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                            with open(output_fimeName, 'wb') as file:
                                                file.write(pdf_content)

                                            pdf_content = get_response_with_retry(xml_link, headers=headers).content
                                            output_fimeName_xml = os.path.join(current_out, f"{pdf_count}.xml")
                                            with open(output_fimeName_xml, "wb") as file:
                                                file.write(requests.get(xml_link, headers=headers).content)

                                            data.append(
                                                {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                 "ItemID": "",
                                                 "Identifier": "",
                                                 "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                 "Article_Number": article_number, "Special Issue": "", "Page Range": "", "Month": month,
                                                 "Day": "",
                                                 "Year": year,
                                                 "URL": article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                                                 "XML File Name": f"{pdf_count}.xml", "user_id": user_id, "TOC File Name": f"{source_id}_TOC.html"})
                                            df = pd.DataFrame(data)
                                            df.to_excel(out_excel_file, index=False)
                                            pdf_count += 1
                                            scrape_message = f"{article_link}"
                                            completed_list.append(scrape_message)
                                            with open('completed.txt', 'a', encoding='utf-8') as write_file:
                                                write_file.write(article_link + '\n')
                                            print("Original Article:", article_link)

                    except Exception as error:
                        message = f"Error link - {article_title}: {str(error)}"
                        print(f"{article_title}: {str(error)}")
                        error_list.append(message)

                try:
                    try:
                        response_en = get_response_with_retry(toc_url, headers=headers)
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
                        url_cn = toc_url.replace('/en', '/cn')

                        response_cn = get_response_with_retry(url_cn, headers=headers)
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

                    output_file = os.path.join(current_out, f"{source_id}_TOC.html")
                    with open(output_file, 'w', encoding='utf-8') as file:
                        file.write(combined_content)

                    print(f"Combined file saved: {output_file}")

                except Exception as e:
                    print(f"Error in creating the TOC file: {e}")
                    error_list.append(f"Error in creating the TOC file: {e}")

                for attempt in range(25):
                    try:
                        common_function.sendCountAsPost(source_id, Ref_value, str(Total_count), str(len(completed_list)),
                                                        str(len(duplicate_list)), str(len(error_list)))
                        break
                    except Exception as error:
                        if attempt == 24:
                            error_list.append(f"Failed to send post request : {str(error)}")

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
                    message = f"Failed to send email: {str(error)}"
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
    Error_message = "Error in the urlDetails.txt f ile :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)