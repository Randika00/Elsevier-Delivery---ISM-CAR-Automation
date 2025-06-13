import re
import requests
import cloudscraper
from bs4 import BeautifulSoup
import os
import common_function
import pandas as pd
from datetime import datetime
import calendar

scraper = cloudscraper.create_scraper()

def extract_volume_issue(text):
    try:
        pattern = r"Volume (\d+), Issue (\d+)"

        match = re.search(pattern, text)
        if match:
            volume = match.group(1)
            issue = match.group(2)
            return volume, issue
        else:
            raise ValueError("Pattern not found in the input string")
    except Exception as e:
        print(f"An error occurred while extracting volume and issue: {e}")
        return None, None

def get_soup(url):
    response = scraper.get(url)
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


def get_token(url):
    response = requests.get(url, headers=headers)
    cookie = response.cookies
    token = cookie.get("wkxt3_csrf_token").replace("-", "")
    return token


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
        url, url_id = url_list[url_index].split(',')
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print_bordered_message("🔍 Scraping in progress... Continuing with ID: " + url_id)
            ini_path = os.path.join(os.getcwd(), "REF_632.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "632"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        attachment = None
        pdf_count = 1

        soup=get_soup(url)
        current_issue_link = soup.find("div",class_="inner-nav desktop-nav pull-left").find("ul",class_="clearlist fontweight-600").find_all('a')[2].get("href")

        soup2 = get_soup(current_issue_link)
        try:
            year =soup.find("div", class_="media-left pull-left text-center pt-50").find("h5", class_="mb-0").text.split()[-1]
            print(f"Extracted Year: {year}")
            date_text = soup.find_all("div", class_="media-body")[1].find("li",class_="col-xs-4").find("a").get_text(strip=True).split("(")[1].split()[0]
            month = calendar.month_name[list(calendar.month_abbr).index(date_text)]
            print(f"Extracted Month: {date_text} ({month})")
            h1_text = soup2.find("h1").text

            volume = h1_text.split(",")[0].split()[-1]
            issue = h1_text.split(",")[1].split()[-1]

            print(f"Extracted Volume: {volume}")
            print(f"Extracted Issue: {issue}")
        except Exception as e:
            print(f"An error occurred in the main function: {e}")


        All_articles =soup2.find_all("div",class_="t-post-content")
        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index + 1
            Article_link, Article_title = None, None
            try:
                Article_link = All_articles[article_index].find("h2", class_="post-title").find("a").get("href")
                Article_title = All_articles[article_index].find("h2", class_="post-title").find("a").get("title")
                doi = All_articles[article_index].find("p", class_="mb-2").find("a").get_text(strip=True)
                pdf_link = All_articles[article_index].find("a",title="PDF").get("href")

                pdf_page=get_soup(Article_link)
                try:
                    # Extract the first page
                    first_page_tag = pdf_page.find("meta", {"name": "citation_firstpage"})
                    last_page_tag = pdf_page.find("meta", {"name": "citation_lastpage"})

                    if first_page_tag and last_page_tag:
                        first_page = first_page_tag.get("content")
                        last_page = last_page_tag.get("content")

                        # Construct the page range
                        page_range = f"{first_page}-{last_page}"
                        print(f"Page Range: {page_range}")
                    else:
                        raise ValueError("First page or last page meta tags not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")

                if article_check == 0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")

                print_bordered_message(f"DOI: {doi},pdf_link:{pdf_link}")

                check_value, tpa_id = common_function.check_duplicate(doi, Article_title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID: {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count) + " article is a duplicate\nArticle title: " + Article_title + "📚\n")

                else:
                    print("Wait until the PDF is downloaded")
                    error_variable = "pdf download"
                    session = requests.Session()
                    retries = 0
                    max_retries = 5
                    download_successful = False

                    while retries < max_retries and not download_successful:
                        response = session.get(pdf_link)
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

                    print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")
                    if download_successful:
                        error_variable = "write excel"
                        data.append({
                            "Title": Article_title, "DOI": doi, "Publisher Item Type": "", "ItemID": "",
                            "Identifier": "", "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                            "Special Issue": "", "Page Range": page_range, "Month": month, "Day": "",
                            "Year": year, "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf",
                            "user_id": user_id
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
                if article_check < 10:
                    article_check += 1
                else:
                    message = f"{Article_link} - Error in {error_variable} for {Article_title}: [{str(error)}]"
                    print(get_ordinal_suffix(Article_count) + " article could not be downloaded due to an error\nArticle title: " + Article_title + "❌\n")
                    error_list.append(message)
                    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)
                    article_index, article_check = article_index + 1, 0




        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),str(len(duplicate_list)), str(len(error_list)))
        except Exception as error:
                error_list.append(f"Failed to send post request: {str(error)}")
                print(error)
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date,current_time, Ref_value)

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
        if url_check < 10:
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
        subject, error_html_content = common_function.email_body(current_date, current_time, duplicate_list,error_list, completed_list,len(completed_list), url_id, Ref_value)
        error_file_path = os.path.join(current_out, 'download_details.html')
        with open(error_file_path, 'w', encoding='utf-8') as file:
            file.write(error_html_content)
        print("Error details file saved to:", error_file_path)
