import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
from urllib3.util.retry import Retry
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
import common_function

source_id = "953484350"

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
            base_url = "http://journal25.magtechjournal.com/Jwk_dzdc/EN"
            toc_url = "http://journal25.magtechjournal.com/Jwk_dzdc/EN/volumn/current.shtml"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_3870.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "3870"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            response = get_response_with_retry(url, headers=headers)
            link = BeautifulSoup(response.content, "html.parser").find("td", {"height": "150", "valign": "top", "bgcolor": "#f4f4f4", "class": "left_bg"}).findAll("td", {"height": "24", "valign": "center"})[1].find("a").get("href").replace("..", "")
            current_link = base_url + link

            response = get_response_with_retry(current_link, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                div_element = soup.find("table", {"height": "156", "width": "98%", "align": "center", "border": "0"}).findAll("table", {"cellspacing": "0", "cellpadding": "0", "width": "100%", "border": "0"})

                Total_count = len(div_element)
                # print(f"Total number of articles: {Total_count}\n")
                processed_titles = set()

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_tag = single_element.find("td", {"valign": "center", "align": "left", "colspan": "2", "height": "22"})

                        if article_title_tag:
                            article_title = article_title_tag.find("b").text.strip()
                            if article_title not in processed_titles:
                                processed_titles.add(article_title)

                                article_link_tag = single_element.find("a", string=re.compile("Abstract"))

                                if article_link_tag:
                                    relative_link = article_link_tag.get('href').replace("..", "")

                                    if not relative_link.startswith('/EN/'):
                                        relative_link = '/EN' + relative_link
                                    article_link = urljoin(base_url, relative_link)

                                doi_tag = single_element.find_all("tr")[3].find("td", {"align": "left", "colspan": "2", "height": "22", "valign": "middle"})
                                doi = ""
                                if doi_tag:
                                    doi_text = doi_tag.get_text(strip=True)
                                    doi_match = re.search(r"DOI: (\S+)", doi_text)
                                    if doi_match:
                                        doi = doi_match.group(1) if doi_text else ""

                                page_range_tag = single_element.find_all("tr")[4]
                                page_range = ""
                                if page_range_tag:
                                    page_range_text = page_range_tag.get_text(strip=True)
                                    page_range_match = re.search(r'(\d+-\d+)', page_range_text)
                                    if page_range_match:
                                        page_range = page_range_match.group(1) if page_range_tag else ""

                                onclick_attr = single_element.find("a", string="PDF")
                                if onclick_attr:
                                    onclick_text = str(onclick_attr)
                                    id_match = re.search(r"lsdy1\('PDF','(\d+)'", onclick_attr['onclick'])
                                    pdf_id = ""
                                    if id_match:
                                        pdf_id = id_match.group(1) if onclick_text else ""

                                    base_pdf_url = "http://journal25.magtechjournal.com/Jwk_dzdc/EN/article/downloadArticleFile.do?attachType=PDF&id="
                                    pdf_link = base_pdf_url + str(pdf_id)

                                    year_volume_issue_info = soup.find("span", class_="STYLE36")
                                    year, volume, issue, month = "", "", "", ""
                                    if year_volume_issue_info:
                                        year_volume_issue_text = year_volume_issue_info.find("strong").get_text(strip=True)

                                        year_match = re.search(r'(\d{4})', year_volume_issue_text)
                                        volume_match = re.search(r'Vol\. (\d+)', year_volume_issue_text)
                                        issue_match = re.search(r'No\. (\d+)', year_volume_issue_text)
                                        month_match = re.search(r'Published: \d{2} (\w+) \d{4}', year_volume_issue_text)

                                        year = year_match.group(1) if year_match else ""
                                        volume = volume_match.group(1) if volume_match else ""
                                        issue = issue_match.group(1) if issue_match else ""
                                        month = month_match.group(1) if month_match else ""

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
                                        data.append(
                                            {"Title": article_title, "DOI": doi, "Publisher Item Type": "",
                                             "ItemID": "",
                                             "Identifier": "",
                                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                                             "Special Issue": "", "Page Range": page_range, "Month": month,
                                             "Day": "",
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
                        url_cn = toc_url.replace('/EN', '/CN')

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
    Error_message = "Error in the urlDetails.txt file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)

