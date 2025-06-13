import os
import time
import random
import requests
import undetected_chromedriver as uc
from cpatche_slover import post_page
import captcha_main
import common_function
from bs4 import BeautifulSoup

# Set headers for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

# Configure Chrome options
# options = uc.ChromeOptions()
# options.add_argument('--incognito')
# options.add_argument('--disable-gpu')
# options.add_argument('--disable-software-rasterizer')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-infobars')
# options.add_argument('--disable-extensions')
# options.add_argument('--disable-popup-blocking')
# options.add_argument('--user-agent=YOUR_USER_AGENT_STRING')
#
# # Initialize the Chrome driver
# driver = uc.Chrome(options=options)

# def captcha_main(url):
#     try:
#         driver.delete_all_cookies()
#         driver.get(url)
#         time.sleep(random.uniform(2, 5))  # Wait for page to load
#         current_url = driver.current_url
#         response = post_page(current_url)  # Assume this returns the URL needed to download the PDF
#         return response
#     except Exception as e:
#         print(f"Error solving CAPTCHA: {e}")
#         return None

def download_pdf(pdf_url, output_dir, pdf_count):
    try:
        # Request PDF content
        pdf_content = requests.get(pdf_url, headers=headers).content

        # Define the output filename
        output_file_name = os.path.join(output_dir, f"{pdf_count}.pdf")

        # Write the PDF content to a file
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
        print(f"Downloaded PDF: {output_file_name}")
    except Exception as e:
        print(f"Failed to download PDF from {pdf_url}: {e}")

# URL of the page with CAPTCHA and PDF
pdf_link = 'https://research.aota.org/ajot/article-pdf/doi/10.5014/ajot.2024.050438/84913/7804185050.pdf'

# Output directory for downloaded PDFs
current_out = 'D:/Innodata/ISM-Car_project/pythonProject/REF_100'

pdf_count = 1

# Solve CAPTCHA and get the resolved URL
# resolved_url = captcha_main(pdf_link)
#
# if resolved_url:
#     # After solving the CAPTCHA, download the PDF
#     download_pdf(resolved_url, current_out, pdf_count)
# else:
#     print("Failed to resolve CAPTCHA and obtain the PDF URL.")
#
# # Clean up and close the driver
# driver.quit()

url_id="100"
ini_path= os.path.join(os.getcwd(),"REF_100.ini")
Download_Path,Email_Sent,Check_duplicate,user_id=common_function.read_ini_file(ini_path)
current_out=common_function.return_current_outfolder(Download_Path,user_id,url_id)
out_excel_file=common_function.output_excel_name(current_out)

# response = requests.get(pdf_link, headers=headers)
# print(pdf_link)
# soup_test = str(BeautifulSoup(response.content, 'html.parser'))
# if soup_test=="Bad Request":
output_file_path = os.path.join(current_out, f"{pdf_count}.pdf")
pdf_response = requests.get(pdf_link, headers=headers)
pdf_content = pdf_response.content

soup_test = str(BeautifulSoup(pdf_content, 'html.parser'))

explanation_message = soup.find('div', class_='explanation-message')

if explanation_message is not None:
    # Solve CAPTCHA if detected
    response = captcha_main.captcha_main(pdf_link)
    pdf_content = response.content
    output_file_path = os.path.join(current_out, f"{pdf_count}.pdf")
    if response.status_code == 200:
        with open(output_file_path, 'wb') as file:
            file.write(pdf_content)
        print(f"PDF downloaded successfully: {output_file_path}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
else:
    # No CAPTCHA detected, save the PDF content
    with open(output_file_path, 'wb') as file:
        file.write(pdf_content)
    print(f"PDF downloaded successfully: {output_file_path}")