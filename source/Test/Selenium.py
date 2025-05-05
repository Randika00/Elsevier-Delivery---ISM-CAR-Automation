import re
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import chromedriver_autoinstaller as chromedriver
import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import common_function
import pandas as pd

chromedriver.install()

script_directory = os.path.dirname(os.path.realpath(__file__))
download_path = os.path.join(script_directory, 'downloads')
if not os.path.exists(download_path):
    os.makedirs(download_path)

def get_driver_pdf(url, new_filename,download_path):
    download_path = download_path

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--user-agent=YOUR_USER_AGENT_STRING')
    options.add_argument('--version_main=108')

    prefs = {'download.default_directory': download_path}
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(50)

    finally:
        driver.quit()

    downloaded_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
    new_file_path = os.path.join(download_path, new_filename)
    shutil.move(downloaded_file, new_file_path)

pdf_link='https://portlandpress.com/clinsci/article-pdf/138/18/1173/961101/cs-2024-1421c.pdf'

get_driver_pdf(pdf_link,"Out.pdf",download_path)