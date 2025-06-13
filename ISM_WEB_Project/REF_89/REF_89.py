import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd
import random
import pdfkit

Total_count=None
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None

def get_soup(url):
    my_proxy = get_random_proxy()
    print(my_proxy)
    response = requests.get(url,headers=headers, proxies=my_proxy)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup


def create_combined_pdf(urls):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    session = requests.Session()
    session.headers.update(headers)

    html_file_path = os.path.join(current_out,TOC_name)

    with open(html_file_path, 'w', encoding='utf-8') as file:
        for url in urls:
            response = session.get(url)
            if response.status_code == 200:
                file.write(f"<!-- Content from {url} -->\n")
                file.write(response.text)
                file.write("\n\n")
            else:
                print(f"Failed to fetch content from {url}. HTTP status code: {response.status_code}")


    print(f"The HTML version of the content has been saved as {html_file_path}.")
pdf_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
headers = {
    "Cache-Control": "no-store",
    "Connection": "Keep-Alive",
    "Content-Encoding": "gzip",
    "Content-Length": "21792",
    "Content-Security-Policy": "frame-ancestors 'self' https://omnidoctor.ru/",
    "Content-Type": "text/html; charset=utf-8",
    "Date": "Tue, 19 Mar 2024 11:11:43 GMT",
    "Keep-Alive": "timeout=10, max=10000",
    "Server": "Apache/2.4.6 (CentOS) mpm-itk/2.4.7-04 OpenSSL/1.0.2k-fips PHP/7.4.33",
    "Strict-Transport-Security": "max-age=31536000; preload",
    "Vary": "Accept-Encoding",
    "X-Frame-Options": "SAMEORIGIN, ALLOW-FROM https://omnidoctor.ru/",
    "X-Powered-By": "PHP/7.4.33",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "RODIN_OJSSID=37c3d4131bc86d43f3ea1868ce12fa7d; currentLocale=en_US; cookieShown=true; _gid=GA1.2.760176992.1710845770; _ym_uid=1710845771103195565; _ym_d=1710845771; _ym_isad=2; _ga_Y7V3G4K7P2=GS1.1.1710845769.1.1.1710846550.0.0.0; _ga=GA1.1.400269993.1710845770",
    "Host": "journals.eco-vector.com",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}


proxies_list = [
    "185.205.199.161:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "216.10.5.126:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "185.207.96.233:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "67.227.121.110:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "67.227.127.100:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "181.177.76.122:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "185.207.97.85:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "186.179.21.77:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "141.98.155.137:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "2.58.80.143:3199:mariyarathna-dh3w3:IxjkW0fdJy",
]

formatted_proxies = [{'http': f'http://{proxy.split(":")[2]}:{proxy.split(":")[3]}@{proxy.split(":")[0]}:{proxy.split(":")[1]}'} for proxy in proxies_list]

def get_random_proxy():
    return random.choice(formatted_proxies)

url_info_list=[]
with open('urlDetails.txt', 'r') as file:
    for line in file:
        url,url_id = line.strip().split(',')
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

        ini_path = os.path.join(os.getcwd(), "REF_89.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)
        Ref_value = "89"
        print(url_id)
        soup = get_soup(url)
        TOC_name = common_function.output_TOC_name(current_out)

        create_combined_pdf(
            [
                "https://journals.eco-vector.com/1682-7392/index",
                "https://journals.eco-vector.com/1682-7392/user/setLocale/ru_RU?source=%2F1682-7392%2Findex",
                "https://journals.eco-vector.com/1682-7392/user/setLocale/zh_CN?source=%2F1682-7392%2Findex"
            ]
        )

        h3_text = soup.find("div", id="currentIssueHome").find("h3").get_text(strip=True)
        pattern = r"Vol (\d+), No (\d+) \((\d{4})\)"
        match = re.match(pattern, h3_text)
        if match:
            volume = match.group(1)
            issue_num = match.group(2)
            year = match.group(3)
        current_issues_link=soup.find("div",class_="titleAuthors").find_all('li')[3].find('a').get("href")
        current_soup = get_soup(current_issues_link)
        all_issues = current_soup.find_all("div", class_=["dark issueArticlesData", "light issueArticlesData"])
        Total_count = len(all_issues)
        print(f"Total number of articles:{Total_count}", "\n")
        article_index, article_check = 0, 0
        while article_index < len(all_issues):
        # for issue in all_issues:
            try:
                Article_link = all_issues[article_index].find('a').get("href")
                Article_title = all_issues[article_index].find('a').get_text(strip=True)
                issue_soup =get_soup(Article_link)
                page_range = issue_soup.find("div", class_="titleAuthors").find_all("li")[-5].get_text(strip=True)
                doi=issue_soup.find("div",class_="titleAuthors").find_all("li")[-2].get_text(strip=True).rsplit('doi.org/',1)[-1]
                pdf_page_url = issue_soup.find("div", id="articleFullText").find("a", class_="file").get("href")
                pdf_soup = get_soup(pdf_page_url)
                pdf_link = pdf_soup.find("div", id="pdfDownloadLinkContainer").find("a", class_="action pdf").get("href")
                check_value,tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue_num)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)
                else:
                    print("Original Article :", Article_title)
                    pdf_content = requests.get(pdf_link, headers=pdf_headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    print(f"Downloaded: {output_fimeName}")
                    data.append(
                        {"Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                         "Volume": volume, "Issue":issue_num, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": "", "Month": "", "Day": "", "Year": year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')
                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"Error link - {Article_link} : {str(error)}"
                    print("Download failed :", Article_title)
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0
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
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
    except Exception as error:
        Error_message = "Error in the site :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)

    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)