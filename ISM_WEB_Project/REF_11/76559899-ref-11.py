import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Cookie": "American_Academy_of_PediatricsMachineID=638449428831762803; fpestid=nArwBRwYpwen-bzYiCaag8sRm0A_svWW40U9_gGnzkypDnE3dLInxu3MP6Aixm8n6CcpkQ; hum_aap_visitor=051d09ad-0048-4508-a2e8-1c2b8667ad1b; __gpi=UID=00000d21489e6c28:T=1709346088:RT=1709603021:S=ALNI_MazpA53OPDPvGmjXGGgijfxpw5PWA; TheDonBot=5594B20C27879DCAEA42EC935B8D2C24; _gid=GA1.2.84935122.1710727021; _ga_G5TCNFJCYP=GS1.1.1710739975.8.1.1710739980.0.0.0; AAP2_SessionId=o1kjtpc4qjzhwqhukr0451hl; feathr_session_id=65f869a976b5029dd255ca8e; _dc_gtm_UA-53057564-11=1; __gads=ID=27717ecb3d043fed:T=1709346088:RT=1710779134:S=ALNI_MbJ7QppOeJzIZIUyi5jKWVOY5JeYA; __eoi=ID=b346539b1b2679fb:T=1709346088:RT=1710779134:S=AA-AfjaxBD07Nk1iaDu9WbKQsKT1; _ga_2162JJ7E97=GS1.1.1710778793.19.1.1710779145.0.0.0; _ga=GA1.1.293847094.1709346089; _ga_FD9D3XZVQQ=GS1.1.1710778793.19.1.1710779145.0.0.0",
    "Host": "publications.aap.org",
    "Referer": "https://publications.aap.org/pediatrics/issue/browse-by-year?autologincheck=redirected",
    "Sec-Ch-Ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}
cookies = {
    'American_Academy_of_PediatricsMachineID': '638449428831762803',
    'fpestid': 'nArwBRwYpwen-bzYiCaag8sRm0A_svWW40U9_gGnzkypDnE3dLInxu3MP6Aixm8n6CcpkQ',
    'hum_aap_visitor': '051d09ad-0048-4508-a2e8-1c2b8667ad1b',
    '__gpi': 'UID=00000d21489e6c28:T=1709346088:RT=1709603021:S=ALNI_MazpA53OPDPvGmjXGGgijfxpw5PWA',
    'TheDonBot': '5594B20C27879DCAEA42EC935B8D2C24',
    '_ga_G5TCNFJCYP': 'GS1.1.1710739975.8.1.1710739980.0.0.0',
    '__gads': 'ID=27717ecb3d043fed:T=1709346088:RT=1711382523:S=ALNI_MbJ7QppOeJzIZIUyi5jKWVOY5JeYA',
    '__eoi': 'ID=b346539b1b2679fb:T=1709346088:RT=1711382523:S=AA-AfjaxBD07Nk1iaDu9WbKQsKT1',
    '_cc_id': '887b3cc2fb5997a3d7d85844831d28a',
    '_ga': 'GA1.1.293847094.1709346089',
    '_ga_2162JJ7E97': 'GS1.1.1711382524.20.1.1711383465.0.0.0',
    '_ga_FD9D3XZVQQ': 'GS1.1.1711382524.20.1.1711383465.0.0.0',
    'AAP2_SessionId': '1fkmoercuvyyp2tcq4skaqgo'
}
pdf_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}

Total_count=None
attachment=None
current_date=None
current_time=None
ini_path=None
duplicate_list = []
error_list = []
data = []
completed_list=[]
url_id="76559899"
pdf_count=1
Ref_value="11"

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url = "https://publications.aap.org/pediatrics/issue/browse-by-year?autologincheck=redirected"

current_datetime = datetime.now()
current_date = str(current_datetime.date())
current_time = current_datetime.strftime("%H:%M:%S")

ini_path= os.path.join(os.getcwd(),"REF_11.ini")
Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
out_excel_file=common_function.output_excel_name(current_out)

page = requests.get(url, headers=headers)
try:
    soup = BeautifulSoup(page.content, 'html.parser')
    content_archive = soup.find('div', class_='navbar-menu_wrap').find_all('a', class_='nav-link')[1]
    href_value = "https://publications.aap.org" + content_archive['href']
    Archive_page = requests.get(href_value, headers=headers)
    Archive_soup = BeautifulSoup(Archive_page.content, 'html.parser')
    volume_issue_span = Archive_soup.find('span', class_='volume issue')
    if volume_issue_span:
        text = volume_issue_span.get_text(strip=True)
        volume, issue = text.split(',')[0].split()[-1], text.split(',')[1].split()[-1]
    else:
        volume = None
        issue = None
    pub_date_div = Archive_soup.find('div', class_='ii-pub-date')
    month, year = pub_date_div.get_text(strip=True).split()
    All_articles = Archive_soup.find_all('div', class_='al-article-items')
    Total_count = len(All_articles)
    print(f"Total number of articles:{Total_count}", "\n")
    for i,section in enumerate(All_articles):
        Article_link = None
        try:
            Article_link = "https://publications.aap.org"+section.find('a').get("href")
            page_url = requests.get(Article_link, headers=headers)
            soup_url = BeautifulSoup(page_url.content, 'html.parser')
            title=soup_url.find('h1',class_='wi-article-title article-title-main').get_text(strip=True)
            doi=soup_url.find('div',class_='citation-doi').find('a').get("href").split("https://doi.org/")[1]
            identifier_tag=soup_url.find('div',class_='ww-citation-primary').get_text(strip=True)
            match = re.search(r'\b[a-z]\d+\b', identifier_tag)
            if match:
                identifier = match.group()
            pdf_link='https://publications.aap.org'+soup_url.find('ul',id="Toolbar").find('li',class_='toolbar-item item-with-dropdown item-pdf').find('a')['href']
            check_value,tpa_id = common_function.check_duplicate(doi, title, url_id, volume, issue)
            if Check_duplicate.lower() == "true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :",title)
            else:
                print("Original Article :", title)
                session = requests.Session()
                session.headers.update(pdf_headers)
                pdf_content = session.get(pdf_link).content
                output_file_name = os.path.join(current_out, f"{pdf_count}.pdf")
                with open(output_file_name, 'wb') as file:
                    file.write(pdf_content)
                print(f"Downloaded: {output_file_name}")
                data.append({"Title": title, "DOI": doi, "Publisher Item Type": "", "ItemID": "", "Identifier": identifier,
                     "Volume": volume, "Issue": issue, "Supplement": "", "Part": "",
                     "Special Issue": "", "Page Range": "", "Month": month, "Day": "", "Year": year,
                     "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                pdf_count += 1
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
            if not Article_link in read_content:
                with open('completed.txt', 'a', encoding='utf-8') as write_file:
                    write_file.write(Article_link + '\n')

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
        common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),ini_path, attachment, current_date, current_time, Ref_value)
    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass
except AttributeError:
    unusual_traffic_message = soup.find('div', class_='explanation-message').text.strip()
    print(unusual_traffic_message)
except Exception as error:
    Error_message = "Error in the site :" + str(error)
    print(Error_message)
    error_list.append(Error_message)

finally:
    subject,error_html_content = common_function.email_body(current_date, current_time, duplicate_list, error_list, completed_list, len(completed_list), url_id, Ref_value)
    error_file_path = os.path.join(current_out, 'download_details.html')
    with open(error_file_path, 'w', encoding='utf-8') as file:
        file.write(error_html_content)

    print("Error details file saved to:", error_file_path)