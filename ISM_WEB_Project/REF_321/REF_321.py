import re
import requests
import json
from bs4 import BeautifulSoup
import os
import common_function
import pandas as pd
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed

def get_soup(url):
    global statusCode
    response = requests.get(url, headers=headers, stream=True)
    statusCode = response.status_code
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def print_bordered_message(message):
    border_length = len(message) + 4
    border = "-" * (border_length - 2)

    print(f"+{border}+")
    print(f"| {message} |")
    print(f"+{border}+")
    print()

def get_ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def download_pdf(url, out_path, headers):
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def get_token(url):
    response = requests.get(url, headers=headers)
    cookie = response.cookies
    token = cookie.get("wkxt3_csrf_token").replace("-", "")
    return token

def dayCheck(day):
    if day.isdigit():
        day = int(day)
        if 1 <= day <= 31:
            return day
    return ""

def monthCheck(month):
    valid_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                    "November", "December"]
    if month in valid_months:
        return month
    return ""

def yearCheck(year):
    if year.isdigit():
        return year
    return ""


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
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
Total_count = None
statusCode = None

try:
    with open('urlDetails.txt', 'r', encoding='utf-8') as file:
        url_list = file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\": " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list), ini_path, attachment, current_date, current_time, Ref_value)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        pass
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')

url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        pre_url, url_id = url_list[url_index].split(',')
        url = "http://ysdw.nefu.edu.cn/api/api/Web/LastIssueList?_t=&PageSize=&PageIndex=0&IssueId=0"
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print_bordered_message("Scraping procedure will continue for ID: " + url_id)
            ini_path = os.path.join(os.getcwd(), "REF_321.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)
        TOC_name = f"{url_id}_TOC.html"

        Ref_value = "321"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        attachment = None
        pdf_count = 1

        All_articles = json.loads(get_soup(url).text)["Data"]

        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}\n")

        html_body_en = ""
        html_body_cn = ""

        first_line = f"{All_articles[0]['PublishYear']} (Volume {All_articles[0]['Volume']}) Issue: {All_articles[0]['IssueNum']}"
        html_body_en += f"<h2>{first_line}</h2>\n"

        first_line_cn = f"{All_articles[0]['PublishYear']}年({All_articles[0]['Volume']}卷)第{All_articles[0]['IssueNumE']}期"
        html_body_cn += f"<h2>{first_line_cn}</h2>\n"

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index + 1
            Article_link, Article_title = None, None
            error_variable = None
            try:
                error_variable = "article link"
                Article_link = f"http://ysdw.nefu.edu.cn/en/#/digest?ArticleID={All_articles[article_index]['ArticleID']}"

                error_variable = "article title"
                Article_title = All_articles[article_index]["TitleE"]

                error_variable = "article metadata"
                Volume = All_articles[article_index]["Volume"]
                Issue = All_articles[article_index]["IssueNum"]
                Year = All_articles[article_index]["PublishYear"]
                DOI = All_articles[article_index]["DOI"]
                Page_range = All_articles[article_index]["Page_Num"] + "-" + All_articles[article_index]["Page_NumEnd"]
                Month, Day = "", ""

                html_body_en += f"<div class='article'>\n"
                html_body_en += f"<a href='{Article_link}' style='text-decoration:none;' color:#00f;'><h3>{Article_title} [{Page_range}]</h3></a>\n"
                html_body_en += f"<p>{All_articles[article_index]['AuthorsListE']}</p>\n"
                html_body_en += f"<p>DOI: <a href='https://doi.org/{DOI}'>{DOI}</a></p>\n"
                html_body_en += f"<p>Summary  View({All_articles[article_index]['View_Times']})  [HTML]({All_articles[article_index]['HtmlRead_Times']}) Export  PDF Download ({All_articles[article_index]['Read_Times']})  Scan the QR code</p>\n"
                html_body_en += "</div>\n"

                html_body_cn += f"<div class='article'>\n"
                html_body_cn += f"<a href='{Article_link}' style='text-decoration:none;' color:#00f;'><h3>{All_articles[article_index]['Title']} [{Page_range}]</h3></a>\n"
                html_body_cn += f"<p>{All_articles[article_index]['AuthorsList']}</p>\n"
                html_body_cn += f"<p>DOI: <a href='https://doi.org/{DOI}'>{DOI}</a></p>\n"
                html_body_cn += f"<p>浏览({All_articles[article_index]['View_Times']})  [HTML]({All_articles[article_index]['HtmlRead_Times']}) 引用 导出  PDF下载({All_articles[article_index]['Read_Times']})  扫码</p>\n"
                html_body_cn += "</div>\n"

                error_variable = "pdf link"
                pdf_link = f"http://ysdw.nefu.edu.cn/api/api/Web/OpenArticleFilebyGuidNew?Id={All_articles[article_index]['PDFFileNameUrlGUID']}"

                if article_check == 0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")

                error_variable = "duplicate check"
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID: {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count) + " article is a duplicate\nArticle title: " + Article_title + "📚\n")

                else:
                    print("Wait until the PDF is downloaded")
                    error_variable = "pdf download"
                    output_fileName = os.path.join(current_out, f"{pdf_count}.pdf")
                    download_pdf(pdf_link, output_fileName, headers)
                    print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")

                    error_variable = "write excel"
                    data.append({
                        "Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                        "Identifier": "", "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                        "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": Day,
                        "Year": Year, "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                        "user_id": user_id, "TOC": TOC_name
                    })

                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print(get_ordinal_suffix(Article_count) + " article is original\nArticle title: " + Article_title + "✅\n")

                if Article_link not in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 30:
                    article_check += 1
                else:
                    message = f"{Article_link} - Error in {error_variable} for {Article_title}: [{str(error)}]"
                    print(get_ordinal_suffix(Article_count) + " article could not be downloaded due to an error\nArticle title: " + Article_title + "❌\n")
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

        # Handle TOC HTML
        check = 0
        while check < 5:
            try:
                print("Wait until the TOC_HTML is downloaded")
                out_html = os.path.join(current_out, TOC_name)
                with open(out_html, 'w', encoding='utf-8') as file:
                    file.write(html_body_en + html_body_cn)
                check = 5
                print("TOC_HTML file downloaded successfully.")
            except:
                if check == 4:
                    message = "Failed to get TOC HTML"
                    error_list.append(message)
                check += 1

        for attempt in range(25):
            try:
                common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),str(len(duplicate_list)), str(len(error_list)))
            except Exception as error:
                if attempt == 24:
                    error_list.append(f"Failed to send post request: {str(error)}")

        try:
            if str(Email_Sent).lower() == "true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)
        except Exception as error:
            message = f"Failed to send email: {str(error)}"
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value, attachment,current_out)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        print_bordered_message("Scraping has been successfully completed for ID: " + url_id)

        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 15:
            url_check += 1
        else:
            try:
                url_index, url_check = url_index + 1, 0
                error_messages = {
                    200: "Server error: Unable to find HTML content",
                    400: "Error in the site: 400 Bad Request",
                    401: "Error in the site: 401 Unauthorized",
                    403: "Error in the site: 403 Forbidden",
                    404: "Error in the site: 404 Page not found!",
                    408: "Error in the site: 408 Request Timeout",
                    500: "Error in the site: 500 Internal Server Error"
                }
                Error_message = error_messages.get(statusCode)

                if Error_message is None:
                    Error_message = "Error in the site: " + str(error)

                print(Error_message, "\n")
                error_list.append(Error_message)
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list), ini_path, attachment, current_date,
                                                     current_time, Ref_value)

            except Exception as error:
                message = f"Failed to send email: {str(error)}"
                print(message)
                common_function.email_body_html(current_date, current_time, duplicate_list, error_list,
                                                completed_list, len(completed_list), url_id, Ref_value,
                                                attachment, current_out)
                error_list.append(message)
    finally:
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list,completed_list, len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)
