import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
import urllib3
from datetime import datetime
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import common_function

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

source_id = "657092712"

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


def get_response_with_retry(url, headers, retries=5, backoff_factor=0.5, status_forcelist=(500, 502, 504), timeout=60, verify_ssl=True):

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

    try:
        response = session.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
        return response
    except requests.exceptions.SSLError as ssl_error:
        print(f"SSL Error encountered for {url}: {ssl_error}")
        print("Retrying with SSL verification disabled...")
        response = session.get(url, headers=headers, timeout=timeout, verify=False)
        return response
    except Exception as e:
        print(f"Error retrieving URL {url}: {e}")
        raise

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
            base_url = "https://www.sjos.cn/EN"
            toc_url = "https://www.sjos.cn/EN/1006-7248/current.shtml"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_305.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "305"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers, verify_ssl=False)
            link = BeautifulSoup(response.content, "html.parser").find("div", class_="zxydpt").findAll("li")[1].find("a").get("href").replace("..", "")
            current_link = base_url + link

            response = get_response_with_retry(current_link, headers=headers, verify_ssl=False)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("div", class_="content_nr").findAll("div", class_="noselectrow")

                Total_count = len(div_element)
                print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("td", {"align": "left", "style": "PADDING-BOTTOM: 3px; PADDING-LEFT: 0px; WIDTH: 100%; PADDING-RIGHT: 0px; VERTICAL-ALIGN: top; PADDING-TOP: 0px"})
                        if article_title_div:
                            article_title = article_title_div.find("a", class_="txt_biaoti").text.strip()
                            article_link = article_title_div.find("a", class_="txt_biaoti").get('href')

                            page_ranges_doi_tag = single_element.find("span", class_="abs_njq")
                            page_range, doi = "", ""
                            if page_ranges_doi_tag:
                                page_ranges_doi_text = page_ranges_doi_tag.get_text(strip=True)

                                page_range_match = re.search(r'(\d{4}, \d+ \(\d+\):\s*([\d-]+))', page_ranges_doi_text)
                                page_range = page_range_match.group(2) if page_range_match else ""

                                doi_match = re.search(r'DOI:\s*(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', page_ranges_doi_text, re.IGNORECASE)

                                doi = doi_match.group(1) if doi_match else ""

                                date_volume_issue_info = soup.find("span", class_="date")
                                day, month, year, volume, issue = "", "", "", "", ""
                                if date_volume_issue_info:
                                    date_volume_issue_text = date_volume_issue_info.get_text(strip=True)

                                    date_volume_issue_match = re.search(
                                        r'(\d{1,2}) (\w+) (\d{4}), Volume (\d+) Issue (\d+)', date_volume_issue_text)
                                    if date_volume_issue_match:
                                        day = date_volume_issue_match.group(1) if date_volume_issue_match else "Date not found"
                                        month = date_volume_issue_match.group(2) if date_volume_issue_match else "Month not found"
                                        year = date_volume_issue_match.group(3) if date_volume_issue_match else "Year not found"
                                        volume = date_volume_issue_match.group(4) if date_volume_issue_match else "Volume not found"
                                        issue = date_volume_issue_match.group(5) if date_volume_issue_match else "Issue not found"

                                    pdf_links = single_element.find_all("a", class_="txt_zhaiyao1")
                                    for link in pdf_links:
                                        onclick_attr = link.get("onclick")
                                        pdf_id_match = re.search(r"lsdy1\('PDF','(\d+)'", onclick_attr)
                                        pdf_id = ""
                                        if pdf_id_match:
                                            pdf_id = pdf_id_match.group(1) if pdf_id_match else ""

                                            base_pdf_url = "https://www.sjos.cn/EN/article/downloadArticleFile.do?attachType=PDF&id="
                                            pdf_link = base_pdf_url + str(pdf_id)

                                            check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                            if Check_duplicate.lower() == "true" and check_value:
                                                message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                                duplicate_list.append(message)
                                                print("Duplicate Article:", article_title)

                                            else:
                                                pdf_content = get_response_with_retry(pdf_link, headers=headers, verify_ssl=False).content
                                                output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                                                with open(output_fimeName, 'wb') as file:
                                                    file.write(pdf_content)
                                                data.append(
                                                    {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                                     "ItemID": "",
                                                     "Identifier": "",
                                                     "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                                     "Special Issue": "", "Page Range": page_range, "Month": month,
                                                     "Day": day,
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
                                                print("Original Article:", article_link)

                    except Exception as error:
                        message = f"Error link - {article_title}: {str(error)}"
                        print(f"{article_title}: {str(error)}")
                        error_list.append(message)

                try:
                    try:
                        response_en = get_response_with_retry(toc_url, headers=headers, verify_ssl=True)
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

                        response_cn = get_response_with_retry(url_cn, headers=headers, verify_ssl=True)
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
                                                    str(len(duplicate_list)), str(len(error_list)))
                except Exception as error:
                    message = f"Failed to send post request: {str(error)}"
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
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
