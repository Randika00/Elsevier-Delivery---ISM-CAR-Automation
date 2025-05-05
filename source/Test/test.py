import cloudscraper
from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import requests
import urllib3

# issues_dates = current_link.find('div', class_='issue-item__header').find_all('span')
#             issues_date = None
#
#             for span in issues_dates:
#                 if re.match(r'\d{2} \w+ \d{4}', span.text.strip()):
#                     issues_date = span.text.strip()
#                     break
#
#             if issues_date:
#                 date_object = datetime.strptime(issues_date, "%d %B %Y")
#                 year = date_object.year
#                 month = date_object.strftime("%B")
#                 day = date_object.day
#             else:
#                 year, month, day = None, None, None
#                 print("No valid date found in issue-item__header")

API_KEY = '7f5e9f5093c12f3065e17ad8b67fb15a'

# dr = webdriver.Chrome()
# dr.get("https://journals.asm.org/toc/spectrum/11/6")
# url='https://journals.asm.org/toc/spectrum/11/6'
# scraper = cloudscraper.create_scraper()
#
# proxy = {
#     # 'http': 'http://893193ea9c931997c248c7ef962b488d7d60358d:port',
#     'https': 'https://893193ea9c931997c248c7ef962b488d7d60358d:port'
# }

# url = "https://journals.asm.org/toc/spectrum/11/6"
# proxy = "http://893193ea9c931997c248c7ef962b488d7d60358d:@proxy.zenrows.com:8001"
# proxies = {"http": proxy, "https": proxy}
# response = requests.get(url, proxies=proxies, verify=False)
# print(response.text)

# Make request using specified proxies
# response = scraper.get('https://example.com', proxies=proxy)
# print(response)
# all_links = bs.find('div', class_='table-of-content').find_all('div',class_='issue-item__title')
# for link in all_links:
#     a_element = link.find('a')
#     href = 'https://journals.asm.org' + a_element.get("href")
#     session = requests.Session()
#     response = session.get(href, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")
#     print(soup)
#     session.close()
# main_link="https://journals.asm.org/loi/spectrum/group/d2020.y2023"
#
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://journals.asm.org/loi/spectrum',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Content-Type": "text/html;charset=UTF-8",
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}


# cookies_string = "MAID='KdWrSUmOuCyh6b+Yq+nUfw==; _gcl_au=1.1.82699383.1703225119; _CEFT=Q%3D%3D%3D; _hjSessionUser_3229557=eyJpZCI6ImUzMGVjZmZkLTU1YzAtNWM1OC1iNGVkLTY4MjY5NTU4YWU0OCIsImNyZWF0ZWQiOjE3MDMyMjUxMjcwNjIsImV4aXN0aW5nIjp0cnVlfQ==; cookiePolicy=accept; _ga_WWL1NVZ78E=GS1.2.1704861670.6.1.1704861705.25.0.0; JSESSIONID=984875a7-9623-4de2-918f-646aa6fb898f; MACHINE_LAST_SEEN=2024-01-10T21%3A46%3A04.515-08%3A00; _gid=GA1.2.483891397.1704951969; _hjIncludedInSessionSample_3229557=0; _hjSession_3229557=eyJpZCI6IjQ2ZDU3NTM4LWVmZDYtNGRhYi1iMmI5LWMwZTU4ZjUyOGE3OCIsImMiOjE3MDQ5NTE5Njg1OTQsInMiOjAsInIiOjAsInNiIjoxfQ==; _hjAbsoluteSessionInProgress=0; _ce.irv=returning; cebs=1; _ce.clock_event=1; _ce.clock_data=202%2C175.157.42.75%2C1%2C9c1ce27f08b16479d2e17743062b28ed; __cf_bm=0YQyFad.kgvsMEA.WA7vxRrs6OL0nk0Kg5hJNMC4gIU-1704953313-1-AUTr6YzLtB9KKH4RROJWu68CwqPq9nQ0Bt3ZjY1nWJRNGdIq6neZTDA5m1mQWUiDauQ3kUQrSUQ64jAShsfUCAI=; cf_clearance=rAwyyc29KLuVj6IorS12JuAxpcU9n.ro6Z8rQuptkE0-1704953327-0-2-30bb6cd2.73e3c79f.52d4ce95-0.2.1704953327; _ga_R5TG0CF1SW=GS1.2.1704951969.4.1.1704953431.60.0.0; _ga=GA1.2.2115372885.1703225121; _dc_gtm_UA-5821458-20=1; _dc_gtm_UA-5821458-23=1; cebsp_=10; __gads=ID=fc802ac023efcd92:T=1703225120:RT=1704953615:S=ALNI_MZllAmW6oZva2TMpN__5zEJz8m4zQ; __gpi=UID=00000cc2eb04e4f4:T=1703537171:RT=1704953615:S=ALNI_MbNWMOK9ttFM8mNid19q0Qws-Wwvw; _ga_PDCJ2KNCPH=GS1.2.1704952511.31.1.1704953619.54.0.0; _ga_143VFX9SE8=GS1.1.1704951968.33.1.1704953619.0.0.0; _ce.s=v~cbe3257101ffd46b04b417984f6dfb7c94788e60~lcw~1704953634950~lva~1704951969555~vpv~12~v11slnt~1704264591122~v11.cs~224058~v11.s~b9ad9690-b044-11ee-b482-69d1592a2a29~v11.sla~1704953634950~gtrk.la~lr8tdaek~v11.send~1704953635333~lcw~1704953635334"
# # Split the string to get individual cookies
# cookie_pairs = cookies_string.split('; ')
#
# # Create a dictionary from the cookie pairs
# cookies = {}
# for pair in cookie_pairs:
#     if '=' in pair:
#         key, value = pair.split('=', 1)
#         cookies[key.strip()] = value.strip()
#
# # Now cookies is a dictionary with your cookies
# print(cookies)

def ret_file_name_full(text, extention):
    exe_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
    out_path = os.path.join(exe_folder, 'in')
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    index = 1
    outFileName = os.path.join(out_path, remove_invalid_paths(text) + extention)
    retFileName = outFileName
    while os.path.isfile(retFileName):
        retFileName = os.path.join(out_path, remove_invalid_paths(text) + "_" + str(index) + extention)
        index += 1
    return retFileName

def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|\n]', "_", path_val)

# pdf_url = 'https://spj.science.org/doi/pdf/10.34133/plantphenomics.0151?download=true'

# all_cookies = pdf_url.get_cookies()
# cookies_disct={}
# for cookie in all_cookies:
#     cookies_disct[cookie['name']] = cookie['value']

# if:
#     # Create a cloudscraper instance
#     scraper = cloudscraper.create_scraper()
#
#     # Use the scraper to get the content
#     pdf_response = scraper.get(pdf_url)
#     output_file_name = ret_file_name_full("Title", '.pdf')
#
#     with open(output_file_name, 'wb') as pdf_file:
#         pdf_file.write(pdf_response.content)
#
#     print(f"Downloaded: {output_file_name}")

# scraper = cloudscraper.create_scraper()
# response = scraper.get(url)
# print(response.text)
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

# Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
# chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
#
# # Set up WebDriver with undetected Chrome options
# driver = webdriver.Chrome(options=chrome_options)
#
# # Navigate to the URL



# # onclick_value = 'f42b69bc-95ff-4f5a-a1d4-08e397781e69'
# base_url = "http://www.spgykj.com/article/exportPdf?id="
pdf_link = "http://www.dwjs.com.cn/1ywuKELSO2ahQuWZ/pr/0/dl/e16f0680-ba8d-4695-a975-ee426c5fc00c.pdf/6LaF5aSn5Z6L5Z+O5biC6Jma5ouf55S15Y6C55qE5pWw5a2X5a2q55Sf5qGG5p626K6+6K6h5Y+K5a6e6Le1LnBkZg==/5paf3o1hxc/0/0"
file_name = "AJPH_PDF.pdf"
# url = "https://www.scielo.br/j/mr/a/8fys6D6YsFVH6FqchdgLrSh/?format=pdf&lang=en"

response = requests.get(pdf_link )
if response.status_code == 200:
    with open(file_name, 'wb') as f:
        f.write(response.content)
    print("PDF downloaded successfully.")









# driver.get(url)
# page_source = driver.page_source
# driver.quit()
#
# # Print or process the page source as needed
# print(page_source)

# scraper = cloudscraper.create_scraper(browser={'custom': 'ScraperBot/1.0'})
# response = scraper.get(pdf_url, headers=headers)
# # Check if the request was successful
# if response.status_code == 200:
#     output_file_name = ret_file_name_full("Title", '.pdf')
#     with open(output_file_name, 'wb') as pdf_file:
#         pdf_file.write(response.content)
#     print(f"Downloaded: {output_file_name}")
# else:
#     print(f"Error: Unable to fetch the PDF. Status code: {response.status_code}")
#     proxy = "http://4c67d85144fee298d117fd02b1d87ebf990d34ea:@proxy.zenrows.com:8001"
#     proxies = {"http": proxy, "https": proxy}
#     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#     response = requests.get(pdf_url, proxies=proxies, verify=False)
#     if response.status_code == 200:
#         output_file_name = ret_file_name_full("Title", '.pdf')
#         with open(output_file_name, 'wb') as pdf_file:
#             pdf_file.write(response.content)
#         print(f"Downloaded: {output_file_name}")
#     else:
#         print(f"Failed to download. Status code: {response.status_code}")





# Proxy settings
# proxy = "http://893193ea9c931997c248c7ef962b488d7d60358d:@proxy.zenrows.com:8001"
# proxies = {"http": proxy, "https": proxy}
#
# # Make the request
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# response = requests.get(pdf_url, proxies=proxies, verify=False)
#
# # Check if the request was successful
# if response.status_code == 200:
#     output_file_name = ret_file_name_full("Title", '.pdf')
#     with open(output_file_name, 'wb') as pdf_file:
#         pdf_file.write(response.content)
#     print(f"Downloaded: {output_file_name}")
# else:
#     print(f"Failed to download. Status code: {response.status_code}")

# url='https://journals.asm.org/toc/spectrum/11/6'
# scraper = cloudscraper.create_scraper(
#     browser={
#         'custom': 'ScraperBot/1.0',
#     }
# )
# response = scraper.get(url, headers=headers)
# soup = BeautifulSoup(response.content, 'html.parser')
# current_links=soup.find('div', class_='table-of-content').find_all('div', class_='issue-item')
# for current_link in current_links:
#     a_element1 = current_link.find('a')
#     title = current_link.find('div',class_='issue-item__title').find('h3').get_text(strip=True)
#     DOI = current_link.find('div', class_='issue-item__doi').find('a').getText(strip=True)
#     Volume_Issue = soup.find('h2', class_='toc__title').text.strip()[:20]
#     issues_date = current_link.find('div', class_='issue-item__header').find_all('span')[1].text.strip()
#     encode_Journal_link = 'https://journals.asm.org' + a_element1.get("href")+'?download=true'
#     print(title)
#     print(issues_date)
#     print(Volume_Issue)
#     print(DOI)
#     print(encode_Journal_link)





# from PyPDF2 import PdfReader
# import re
#
# file_path = 'in\\Title.pdf'
# reader = PdfReader(file_path)
#
# # Extract text from the first page
# first_page_text = reader.pages[0].extract_text()
# relevant_portion = first_page_text[-1000:]  # Extracting the last 1000 characters
#
# # Search again for the pattern "November/December 2023"
# match = re.search(r'November/December 2023', relevant_portion)
# extracted_text = match.group(0) if match else "Text not found"
#
# extracted_text
#
# # Search for the specific pattern in the text
# match = re.search(r'November/December 2023', first_page_text)
# extracted_text = match.group(0) if match else "Text not found"
#
# print(extracted_text)
#
#
# first_page_text = reader.pages[0].extract_text()
# # print(first_page_text)
# pattern = re.compile(r'Published (\d{1,2} \w+ \d{4})')
#
# # match = re.search(pattern, first_page_text)
# match = re.search(r'Volume \d+\s+Issue \d+\s+10\.1128/spectrum\.\d+', first_page_text)
#
# if match:
#     published_info = match.group(0)
#     print(published_info)
# else:
#     print("Published information not found.")


# from PyPDF2 import PdfReader
# import re
# import requests
# from io import BytesIO
#
# pdf_url = 'https://journals.asm.org/doi/pdf/10.1128/spectrum.02567-23?download=true'
#
# proxy = "http://4c67d85144fee298d117fd02b1d87ebf990d34ea:@proxy.zenrows.com:8001"
# proxies = {"http": proxy, "https": proxy}
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# response = requests.get(pdf_url, proxies=proxies, verify=False)
# if response.status_code == 200:
#     reader = PdfReader(BytesIO(response.content))
#
#     # Extract text from the first page
#     first_page_text = reader.pages[0].extract_text()
#     relevant_portion = first_page_text[-1000:]  # Extracting the last 1000 characters
#
#     # Search for the pattern "January 2024" or any other month and year
#     match = re.search(
#         r'(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year>\d{4})',
#         relevant_portion)
#     if match:
#         month = match.group('month')
#         year = match.group('year')
#         print("Month:", month)
#         print("Year:", year)
#     else:
#         print("Text not found")
# else:
#     print("Failed to download the PDF:", response.status_code)

