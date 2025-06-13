import re
import requests
from PyPDF2 import PdfReader
from io import BytesIO
from bs4 import BeautifulSoup
import os
import common_function
import pandas as pd
from datetime import datetime


def get_soup(url):
    response = requests.get(url, headers=headers)
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
        url, url_id = url_list[url_index].split(',')
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print_bordered_message("🔍 Scraping in progress... Continuing with ID: " + url_id)
            ini_path = os.path.join(os.getcwd(), "REF_624.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "624"

        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        attachment = None
        pdf_count = 1

        soup=get_soup(url)

        try:
            date_time_meta=soup.find("span",class_="darkblue-text").get_text(strip=True)
            pattern = r"Vol\. (\d+).*?Nro\. (\d+).*?(\w+) (\d{4})"

            # Match the pattern
            match = re.search(pattern, date_time_meta)

            if match:
                volume = match.group(1)
                issue = match.group(2)
                month_spanish = match.group(3)
                year = match.group(4)

                # Translate month from Spanish to English
                month_translation = {
                    "Enero": "January", "Febrero": "February", "Marzo": "March",
                    "Abril": "April", "Mayo": "May", "Junio": "June",
                    "Julio": "July", "Agosto": "August", "Septiembre": "September",
                    "Octubre": "October", "Noviembre": "November", "Diciembre": "December"
                }
                month = month_translation.get(month_spanish, month_spanish)  # Default to Spanish if not found

                # Output the extracted values
                print(f'volume="{volume}", issue="{issue}", month="{month}", year="{year}"')
            else:
                print("Pattern not found")
        except Exception as e:
            print(f"An error occurred: {e}")

        All_articles =soup.find_all("a", string="Español")
        Total_count = len(All_articles)
        print(f"Total number of articles: {Total_count}\n")

        max_retries = 5
        articles_data = []
        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link, Article_title, pdf_link, doi = None, None, None, None
            try:
                article = All_articles[article_index]

                # english_tag = article.find("a", text="English")
                if article:
                    parent = article.find_parent("p")
                    pdf_link = parent.find_all("a")[-1].get("href")
                    try:
                        pattern = r"10\.\d{4,9}/[\w\.-]+"
                        match = re.search(pattern, pdf_link)

                        if match:
                            doi = match.group(0)
                            print(f"DOI: {doi}")
                        else:
                            print("DOI not found.")
                    except Exception as e:
                        doi=""
                        print("Doi is not there: {e}")


                    if parent:
                        br_tags = parent.find_all("br")
                        for i in range(len(br_tags) - 1):
                            # Look for the English title after the second <br>
                            if "Español" in parent.text and i > 0:
                                Article_title = br_tags[i].next_sibling.strip()
                                break

                    # Append the extracted data
                    if Article_title and pdf_link:
                        articles_data.append({
                            "Article_title": Article_title,
                            "PDF_link": pdf_link,
                            "DOI": doi
                        })
                        print(f"Article {article_index + 1}:")
                        print(f"Title: {Article_title}")
                        print(f"PDF Link: {pdf_link}")
                        print(f"DOI: {doi}\n")

                # Download PDF
                session = requests.Session()
                retries = 0
                download_successful = False
                while retries < max_retries and not download_successful:
                    response = session.get(pdf_link, headers=headers)
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

                if download_successful:
                    data.append({
                        "Title": Article_title, "DOI": doi, "PDF Link": pdf_link, "File Name": f"{pdf_count}.pdf"
                    })
                    print(f"Article {article_index + 1}: {Article_title} ✅")
                    pdf_count += 1
                else:
                    raise ValueError("Failed to download PDF after multiple attempts")

                completed_list.append(pdf_link)

            except Exception as error:
                error_message = f"Error in article {article_index + 1}: {error}"
                print(error_message)
                error_list.append(error_message)

            finally:
                article_index += 1

        # Save data to Excel
        if data:
            df = pd.DataFrame(data)
            df.to_excel(out_excel_file, index=False)
            print(f"Data saved to {out_excel_file}")

        # Summary of Errors and Completed
        print(f"\nCompleted articles: {len(completed_list)}")
        print(f"Errors encountered: {len(error_list)}")
        if error_list:
            print("Errors:", "\n".join(error_list))




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
