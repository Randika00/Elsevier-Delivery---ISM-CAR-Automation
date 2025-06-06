import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import os
import  time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver
chromedriver.install()
import common_function

def first_drive(url,request_cookies):
    driver.get(url)
    content = driver.page_source
    uc_soup = BeautifulSoup(content, 'html.parser')
    return uc_soup

def use_drive(url, request_cookies):
    driver.get(url)
    for cookie_name, cookie_value in request_cookies.items():
        driver.add_cookie({"name": cookie_name, "value": cookie_value})
    driver.refresh()  # Refresh page to ensure cookies are applied
    content = driver.page_source
    uc_soup = BeautifulSoup(content, 'html.parser')
    return uc_soup

def get_pdf_link(pdf_link):
    driver.get(pdf_link)
    time.sleep(2)
    for i in range(30):
        current_url = driver.current_url
        if current_url != pdf_link:
            return current_url
        time.sleep(1)

source_id = "76326399"

cookie = {
    "gtinfo": {
        "ct": "Havelock Town",
        "c": "null",
        "cc": "null",
        "st": "1",
        "sc": "36192",
        "z": "00500",
        "lat": "6.89",
        "lon": "79.86",
        "dma": "-1",
        "cntr": "lka",
        "cntrc": "144",
        "tz": "null",
        "ci": "116.206.246.228"
    },
    "AMCVS_16AD4362526701720A490D45%40AdobeOrg": "1",
    "s_ecid": "MCMID%7C86977521470210699451323184384895867616",
    "oauth_access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImZjZWMxNDVhYjZmMWI3M2U1ZTU3ZGEwMDg0MjE3ODRhZWNhMjZkMzMyY2NmNjE2YmE5NzBjYmU4ODEzNDI2NzEwMmRhOTVhNjRkMTg0ZTNhIn0.eyJhdWQiOiI2ZmRmOGEyMy1lYjc4LTQ5YjctYjNjYS05NzlkMzdlYzI3MWYiLCJqdGkiOiJmY2VjMTQ1YWI2ZjFiNzNlNWU1N2RhMDA4NDIxNzg0YWVjYTI2ZDMzMmNjZjYxNmJhOTcwY2JlODgxMzQyNjcxMDJkYTk1YTY0ZDE4NGUzYSIsImlhdCI6MTcyOTQ4NDY0NywibmJmIjoxNzI5NDg0NjQ3LCJleHAiOjE3MzA2OTQyNDcuMzMzOTg3LCJzdWIiOiIxNDM5NzgiLCJzY29wZSI6WyJhdXRoZW50aWNhdGVkIiwicmVzdF9hcGkiXX0.Lx-LIfq75lhvUnEzmUuufh5K_uzRIsMS2xUgmS428AFclEi1sXmdElgeA7hgD7BWKwdq-CJjmvSYuS9n59QjPu5w2pp9g_zS3eVW-y6HgKC0g2Mw1FrLEAliLwMz4zHXBRlHMlYDyzk-mnm-LDcgJjLsZhdK5RPHEl5xvp21min0qv7JsKuvvaQaRI9MGN7sImvrYhMrfZMDNcIZ4SHHoBoE3PnB-Wk8ozFYKPieZlSkWYOuHe1v6rOTd7BCipmH7MKQKI4uMekOSqCzHbn50DMHjdSUzSnGrvTNWCa-iO9aisXtXxpw5xW_c9CzEDXNih2TVbdRvZj6EQXvitDhRKKqHDWn7e2Mpu7tQa2vUBXRa4CKjdT2i0CMgqFs5Vd_eXvd7KtB7xDZ9EdhUKsi4tTwh_2o_2qTDKnWhRa6cAFU0l19uI8QK02FbEtdOpC0ONAc1FJLF4y5NwnRmc43Oar6ULBXBX7byd7Z_VyqJ7btmvzsEirEVTGUvBPW0W5Rwh20yN7drn_ukItWxb1VCdpat0l3kGfk23aaMbyTLMyNpiDvubmmZb9D_j14ZXvtE8v7Vb1FR3qypbtSzrxktNfjkYQDQsVoSEgAaJBUNcoHAN1-7NWEdvaXnkhjD3b8Cfcoorim6z7dKqZHJgPgg3NEKqzNDLRDXqjvwYZ-jJQ",
    "ppid": "ye5INbym3bjRhZOuchkWK4FVSYJi80w2SmtRBdplTS1729484649",
    "s_cc": "true",
    "_cc_id": "c97b8ec6c52ea8b9dede8a7a3c14dc29",
    "panoramaId_expiry": "1730089452649",
    "panoramaId": "b15b256dbd15c31c8b58b8c1a5eb185ca02cd7e719043eda8d246296516c5464",
    "panoramaIdType": "panoDevice",
    "lrt_wrk": "lrt_medscape_router_4_19R_3W_2024-10-14_13:28:55_gec:0:ecroute:0_cookiestrip_true_ec:0:k8s_resp:k8s:200_OT:false:noMatch_gtS:1:htmsrc:k8sso",
    "__mdscp_vcdt": "Mon Oct 21 2024 09:54:57 GMT+0530 (India Standard Time)",
    "__mdscp_vc": "2",
    "has_js": "1",
    "STYXKEY__mdedge_session_start": "1",
    "_gid": "GA1.2.1320121547.1729490849",
    "pushly.user_puuid": "CoQEr5vM6UpBd9G5Ek9afoAdKRbk8dXh",
    "_ga": "GA1.1.276526477.1729490849",
    "pulse_point_geo_loc": "2",
    "_pnlspid": "31213",
    "_pnss": "dismissed",
    "_pnpdm": "true",
    "_ga_SD9LLJRQ7D": "GS1.1.1729490854.1.1.1729490871.0.0.0",
    "med_session": "uks0nqa5mdwaNMoZj3FGVlrBTUWqHbmp8kPq3lSRylHW9ZKpFDcLeAwcboh%2BcDh6oNnGP9eBgqHMMLqPtVsRhoUyI%2FE255oVEXoV14K35zKl3HuLKIwB5T0C51Y5aS3mBiUTxl%2FAYdNdZNAHaFMqpLwIDhnIgg6DagqIRi8TXasEunusc%2FRY%2BIsGiX5hLXeu%2BzR7JOvv8aVr%2FQrhIxI%2F4EYUI9SaRkxQdcSiIZbST4COInDUJI%2BkBxialjLBgqbMRcoMbhbEaiZ8L4tYvlHyrXoD4uzjgr5%2Bk9NTKAOWP%2BI9q3B5iCTTdvhcPwmp0gzZr8Qz2AdKO9zhh0zt2xDQ7s3nHlvepMi5N36Vn4tCvfJaqwODd%2BHE7PCfJAYTlfAM3Vw9BNQWB5LSGTxJCHDZMnxWXnrJnQSOSNmIDpSeEdo%3D",
    "PIMC": "0",
    "EXPIRY_TIME": "Mon, 21 Oct 2024 08:01:26 GMT",
    "s_sq": "[[B]]",
    "AMCV_16AD4362526701720A490D45%40AdobeOrg": "-2121179033%7CMCIDTS%7C20018%7CMCMID%7C86977521470210699451323184384895867616%7CMCAAMLH-1730100686%7C3%7CMCAAMB-1730100686%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1729503086s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.3.0",
    "s_ips": "602.8000030517578",
    "s_tp": "2110",
    "s_ppv": "mdedge.com%252Fdermatology%252Fissue%252F271067%252Fcutis-1144%2C100%2C29%2C2110%2C5%2C7"
}

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

check = 0
while check < 10:
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

        options = uc.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--incognito')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={user_agent}')

        driver = uc.Chrome(options=options)

        check = 10
    except Exception as error:
        if not check < 9:
            message = "Error in the Chrome driver. Please update your Google Chrome version."
            error_list.append(message)
            common_function.attachment_for_email(source_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
        check += 1

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
            base_url = "https://www.mdedge.com"

            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            ini_path = os.path.join(os.getcwd(), "Ref_1150.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, source_id)
            out_excel_file = common_function.output_excel_name(current_out)
            Ref_value = "1150"
            print(source_id)

            duplicate_list = []
            error_list = []
            completed_list = []
            data = []
            pdf_count = 1

            try:
                current_soup = first_drive(url, cookie)
                current_link = current_soup.find_all("div", class_="year-flexbox")[-1].find("div", class_="issue-month").find("a").get("href")
            except:
                current_soup = use_drive(url, cookie)
                current_link = current_soup.find_all("div", class_="year-flexbox")[-1].find("div", class_="issue-month").find("a").get("href")

            try:
                soup = first_drive(current_link, cookie)

            except:
                soup = use_drive(current_link, cookie)

            if True:
                div_element = soup.find("section", class_="issue-article-section").findAll("div")
                Total_count = len(div_element)
                # print(f"Total number of articles: {Total_count}\n")

                for single_element in div_element:
                    article_link, article_title = None, None
                    try:
                        article_title_div = single_element.find("div", class_="article-flexbox")
                        if article_title_div:
                            article_title = article_title_div.find("a", class_="item-title").text.strip()
                            article_link = article_title_div.find("a", class_="item-title").get('href')

                            volume_issue_date_info = soup.find("div", class_="content")
                            volume, issue, month, year = "", "", "", ""
                            if volume_issue_date_info:
                                text_content = volume_issue_date_info.text.strip()

                                match = re.search(r'(\b\w{3}\b),\s*(\d{4})Vol\.\s*(\d+)(?:No\.\s*(\d+))?', text_content)
                                if match:
                                    month_abbr = match.group(1) if text_content else ""
                                    year = match.group(2) if text_content else ""
                                    volume = match.group(3) if text_content else ""
                                    issue = match.group(4) if text_content else ""

                                    month_mapping = {
                                        "Jan": "January", "Feb": "February", "Mar": "March",
                                        "Apr": "April", "May": "May", "Jun": "June",
                                        "Jul": "July", "Aug": "August", "Sep": "September",
                                        "Oct": "October", "Nov": "November", "Dec": "December"
                                    }

                                    month = month_mapping.get(month_abbr, month_abbr)

                                try:
                                    last_soup = first_drive(article_link, cookie)
                                except:
                                    last_soup = use_drive(article_link, cookie)

                                if True:
                                    pages_doi_tag = last_soup.find("div", class_="article-eyebrow")
                                    page_range, doi = "", ""

                                    if pages_doi_tag:
                                        citation_tag = pages_doi_tag.find("div", class_="article-citation")
                                        if citation_tag:
                                            pages_doi_text = citation_tag.text.strip()

                                            match = re.search(r'(\d+(-\d+)?(,\s*\d+(-\d+)?)*)\s+\|\s+doi:(\S+)', pages_doi_text)
                                            if match:
                                                page_range = match.group(1) if pages_doi_text else ""
                                                doi = match.group(5) if pages_doi_text else ""
                                            else:
                                                print("No match found for page range and DOI.")
                                        else:
                                            print("Citation tag not found.")

                                    pdf_url_text = last_soup.find("div", class_="pagination-article")
                                    pdf_link = ""
                                    if pdf_url_text:
                                        pdf_link = pdf_url_text.find("a", class_="download-article").get('href') if pdf_url_text else ""

                                        check_value, tpa_id = common_function.check_duplicate(doi, article_title, source_id, volume, issue)

                                        if Check_duplicate.lower() == "true" and check_value:
                                            message = f"{article_link} - duplicate record with TPAID: {tpa_id}"
                                            duplicate_list.append(message)
                                            print("Duplicate Article:", article_title)

                                        else:
                                            # updatedLink = get_pdf_link(pdf_link)
                                            pdf_content = requests.get(pdf_link, headers=headers).content
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
                                                 "user_id": user_id})
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