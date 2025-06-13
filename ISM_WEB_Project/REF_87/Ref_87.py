import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}
pdf_count = None
Total_count = None

def extract_title_from_h2(h2_element):
    title = ""
    for child in h2_element.contents:
        if child.name == 'i':
            title += " " + child.get_text(strip=True)
        elif child.name == 'sub':
            title += " " + child.get_text(strip=True)
        elif child.name != 'span':
            title += " " + str(child)
    return title.strip()

def extract_info(text):
    volume_match = re.search(r'Volume:\s*(\d+)', text)
    volume = volume_match.group(1) if volume_match else None
    issue_match = re.search(r'Issue:\s*(\d+)', text)
    issue = issue_match.group(1) if issue_match else ""
    year_match = re.search(r'Published:\s*(\d{4})', text)
    year = year_match.group(1) if year_match else None
    return volume, issue, year

def process_articles(current_issue_url, Check_duplicate):
    global pdf_count
    try:
        current_page = requests.get(current_issue_url, headers=headers, timeout=100000)
        current_soup = BeautifulSoup(current_page.content, 'html.parser')
        text_element = current_soup.find("div", class_="col content issueIndex").find("strong",class_="h6 fw-bold d-block mb-3")
        if text_element:
            text = text_element.get_text(strip=True)
        else:
            text = None
        volume, issue, year = extract_info(text)
        li_elements = current_soup.find_all('td', class_="pt-4 pb-4")
        Total_count = len(li_elements)
        print(f"Total number of articles:{Total_count}", "\n")
        article_index, article_check = 0, 0
        while article_index < len(li_elements):
            try:
                Article_url = "https://www.scielo.br" + li_elements[article_index].find("ul", class_="nav mt-3").find_all('a')[-2].get('href')
                pdf_link = "https://www.scielo.br" + li_elements[article_index].find("ul", class_="nav mt-3").find_all('a')[-1].get('href')
                Article_page = requests.get(Article_url, headers=headers)
                Article_soup = BeautifulSoup(Article_page.content, 'html.parser')
                title = Article_soup.find("h1", class_='article-title').get_text(strip=True)
                doi = Article_soup.find("a", class_="_doi").get_text(strip=True).rsplit("org/", 1)[-1]
                check_value, tpa_id = common_function.check_duplicate(doi, title, url_id, volume, "")
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_url} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", title)
                else:
                    print("Original Article :", title)
                    session = requests.Session()
                    session.headers.update(headers)
                    retries = 0
                    max_retries = 10
                    download_successful = False

                    while retries < max_retries and not download_successful:
                        response = session.get(pdf_link, headers=headers)
                        pdf_content = response.content

                        output_file_name = os.path.join(current_out, f"{pdf_count}.pdf")
                        with open(output_file_name, 'wb') as file:
                            file.write(pdf_content)

                        if os.path.getsize(output_file_name) > 0:
                            print(f"Downloaded: {output_file_name}")
                            download_successful = True
                        else:
                            retries += 1
                            print(f"Retrying download... Attempt {retries}/{max_retries}")

                    if download_successful:
                        data.append({
                            "Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                            "Identifier": "", "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                            "Special Issue": "", "Page Range": "", "Month": "", "Day": "", "Year": year,
                            "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id
                        })

                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_url}"
                        completed_list.append(scrape_message)
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_url + '\n')
                article_index, article_check = article_index + 1, 0
            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"Error link - {Article_url} : {str(error)}"
                    print("Download failed :", title)
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0
    except Exception as error:
        message = f"Error processing articles for URL {url}: {str(error)}"
        error_list.append(message)
        print(error)

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
        user_id = os.getlogin()

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "REF_87.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        Ref_value = "87"
        print(url_id)
        page = requests.get(url, headers=headers, timeout=100000)
        soup = BeautifulSoup(page.content, 'html.parser')
        if url_id != "78463099":
            current_issue_url = "https://www.scielo.br" + soup.find('tbody').find('td', class_='left').find_all('a')[-1].get("href")
            process_articles(current_issue_url, Check_duplicate)
        else:
            current_issue_urls = soup.find('tbody').find('td', class_='left').find_all('a')
            for current_issue_url in current_issue_urls:
                try:
                    current_issue_url1 = "https://www.scielo.br" + current_issue_url.get("href")
                    process_articles(current_issue_url1, Check_duplicate)
                except Exception as error:
                    message = f"Error processing articles for URL {url}: {str(error)}"
                    error_list.append(message)
                    print(error)
                    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

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
