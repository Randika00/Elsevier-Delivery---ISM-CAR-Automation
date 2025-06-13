import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Cookie": "ASMEDC_SessionId=2oew3qtyi42ftulg0fexrxnp; ASME_Digital_CollectionMachineID=638566346566984256; cf_clearance=3NMbd2ngMAfVmtN7x8GNIQ18RVqM5gAYAginc4bpJhQ-1721037861-1.0.1.1-b3RzGg51pALXsWegEH4CyAM7VS9LsnW.tdyl2YuRYlfKP46jfMo8YTBLQmct8Mz4jxEwDjy493AczbNQ8KI.dQ; sf_usid=YWZhOTEwMzMtMzQxOS00ZGE2LWJmYzEtNjdlOGM4OGVlMmRk; SsoCookie=https://asmedigitalcollection.asme.org/memagazineselect/issue/145/5; __cf_bm=UO7hPYXRIbfaSRCT0AKFcRAmTADmFBENU9KuimkY7do-1721041684-1.0.1.1-rRB1eaUHNcLnSDz0d.67.ZomT4IoOFA2Ywo_P1rYJh7C3Ch02gifwxd3SO.mxGPzt5dPGsNRLkW8bzI3LIlKHQ",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

pdf_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def get_soup(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


current_date = None
current_time = None
ini_path = None
Total_count = None
Ref_value = "246"

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url_info_list = []
with open('urlDetails.txt', 'r') as file:
    for line in file:
        url, url_id = line.strip().split(',')
        url_info_list.append({"url": url, "url_id": url_id})

for url_info in url_info_list:
    try:
        url = url_info["url"]
        url_id = url_info["url_id"]

        attachment = None
        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        pdf_count = 1

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "REF_246.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)

        retries = 0
        max_retries = 10
        soup = None

        while retries < max_retries:
            try:
                soup = get_soup(url)
                vol_iss_text = soup.find("div", class_="volume-issue__wrap").find("a").find("span",class_="volume issue").get_text(strip=True)
                pattern = r'Volume (\d+), Issue (\d+)'
                match = re.search(pattern, vol_iss_text)
                if match:
                    volume = match.group(1)
                    issue = match.group(2)
                else:
                    raise ValueError("Pattern not found in the string.")

                month_year_text = soup.find("div", class_="ii-pub-date").get_text(strip=True)
                month_year_text = month_year_text.strip("'")
                pattern = r"(\w+)\s+(\d{4})"
                match = re.search(pattern, month_year_text)
                if match:
                    month = match.group(1)
                    year = match.group(2)
                    print(f'month="{month}", year="{year}"')
                else:
                    raise ValueError("Pattern not found in the string.")

                content_archive = soup.find_all('div', class_="al-article-items")
                Total_count = len(content_archive)
                print(f"Total number of articles: {Total_count}\n")
                break

            except Exception as error:
                retries += 1
                print(f"Attempt {retries}/{max_retries} failed: {str(error)}")
                if retries == max_retries:
                    raise error

        for element in content_archive:
            Article_link = None
            try:
                Article_link = "https://asmedigitalcollection.asme.org" + element.find("h5",class_="customLink item-title").find("a").get('href')
                title = element.find("h5", class_="customLink item-title").find("a").get_text(strip=True)
                text = element.find("div", class_="ww-citation-primary").get_text(strip=True)

                page_range_match = re.search(r'(\d+–\d+)', text)
                page_range = page_range_match.group(1) if page_range_match else "Not found"

                doi_text = soup.find("span", class_="citation-label").get_text(strip=True)
                pattern = r'doi\.org/(10\.\d{4}/[\w.-]+)'
                match = re.search(pattern, doi_text)
                if match:
                    doi = match.group(1)
                else:
                    raise ValueError("DOI not found in the URL.")

                pdf_link = "https://asmedigitalcollection.asme.org" + element.find("a",class_="al-link pdf openInAnotherWindow stats-item-pdf-download js-download-file-gtm-datalayer-event article-pdfLink").get('href')
                check_value, tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article:", title)
                else:
                    session = requests.Session()
                    retries = 0
                    max_retries = 5
                    download_successful = False

                    while retries < max_retries and not download_successful:
                        response = session.post(pdf_link, headers=pdf_headers)
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
                        data.append(
                            {"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                             "Volume": volume, "Issue": issue, "Supplement": "", "Part": "", "Special Issue": "",
                             "Page Range": page_range, "Month": month, "Day": "", "Year": year, "URL": Article_link,
                             "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print("Original Article:", title)

            except Exception as error:
                message = f"Error link - {Article_link} : {str(error)}"
                error_list.append(message)
                print(error)

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),str(len(duplicate_list)), str(len(error_list)))
        except Exception as error:
            message = str(error)
            error_list.append(message)

        if str(Email_Sent).lower() == "true":
            attachment_path = out_excel_file
            if os.path.isfile(attachment_path):
                attachment = attachment_path
            else:
                attachment = None
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,len(completed_list), ini_path, attachment, current_date, current_time,Ref_value)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass

    except Exception as error:
        Error_message = "Error in the site :" + str(error)
        print(Error_message)
        error_list.append(Error_message)
        common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,len(completed_list), url_id, Ref_value, attachment, current_out)
