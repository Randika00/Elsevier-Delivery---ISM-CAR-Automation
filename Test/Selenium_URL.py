from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller as chromedriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

# Automatically install the correct version of ChromeDriver
chromedriver.install()

# Create a WebDriver instance
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

# Initialize the WebDriver with the automatically installed ChromeDriver
driver = webdriver.Chrome(options=options)

# Specify the URL
url = "https://zrxuebao.njust.edu.cn/"

try:
    # Navigate to the URL
    driver.get(url)

    # Wait for a few seconds to allow the page to load completely
    time.sleep(5)

    # Get the page source
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    # header_text = soup.find("div", class_="n-j-q")
    print(soup)

finally:
    # Close the browser
    driver.quit()