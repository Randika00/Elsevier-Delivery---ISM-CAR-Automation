import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller as chromedriver
from twocaptcha import TwoCaptcha
import time

# Initialize 2Captcha solver with your API key
solver = TwoCaptcha('a03589ed562de14589af1d772c2b41bb')

cookies = {
    "_hjSession_360107": "eyJpZCI6IjU2ZTI2ODg1LWZiYmEtNGRmNy05MGMxLTc5NzlhZTFlMjZjYiIsImMiOjE3MTg3NjI1MTk5NzAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=",
    "_hjSessionUser_360107": "eyJpZCI6IjExZWNkNTIwLWNlZGUtNWIxMC05OGM3LTI4OGFlZDc2MTgxNyIsImNyZWF0ZWQiOjE3MTg3NjI1MTk5NjksImV4aXN0aW5nIjpmYWxzZX0=",
    "_ga_1G284LDK06": "GS1.1.1718762518.1.0.1718762518.0.0.0",
    "__utmt": "1",
    "__utma": "136797536.1526303384.1718762517.1718762517.1718762517.1",
    "__cf_bm": "InH6IwgbnBysGzHe76M2s7GAQAmmO_yNT9DJhkJd1PQ-1718762516-1.0.1.1-n5yUpVPP5e5DHhVJuRZvbWIMA3csNXGlRqc3GgyD7GsVFKy0bEFwuVJyDDqpsHxvuKLztzmdcEhohXntFwO._Q",
    "__utmb": "136797536.1.10.1718762517",
    "timezone": "330",
    "__utmz": "136797536.1718762517.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
    "JSESSIONID": "04DF41D5A2FC6ECB776D9C8BB626F98D",
    "MACHINE_LAST_SEEN": "2024-06-18T19%3A01%3A56.196-07%3A00",
    "MAID": "UoIABx3nY/mh6b+Yq+nUfw==",
    "cf_clearance": "hpxV4fZM8HptNTaEpixG73dBXIZLVfa.a8yAQA9b6jI-1718762520-1.0.1.1-X3VrNFR6oPSzJO4nwHoR6bbjXK8g8r9yny_5BQDdPcemu2vs9hdge2MNs78u3eR6u9u1FOJ9arlKvGtv37NsLA",
    "_ga": "GA1.1.906992827.1718762519",
    "__utmc": "136797536",
    "JSESSIONID": "04DF41D5A2FC6ECB776D9C8BB626F98D"
}

def get_soup_using_requests(url, headers, cookies):
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# Function to solve CAPTCHA using 2Captcha
def solve_captcha(site_key, url):
    try:
        result = solver.recaptcha(sitekey=site_key, url=url)
        captcha_solution = result['code']
        return captcha_solution
    except Exception as e:
        print(f'Error solving CAPTCHA: {e}')
        return None

# Set up Selenium WebDriver
chromedriver.install()
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1400,600")
chrome_options.add_argument("--incognito")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

main_link = 'https://ajph.aphapublications.org/'
soup = get_soup_using_requests(main_link, headers, cookies)
current_issue_ele = soup.find("div", class_="navContainer").find("ul", class_="subnav").find_all("li")[1].find("a").get("href")
current_issue_link = "https://ajph.aphapublications.org" + current_issue_ele

# Navigate to the current issue link
driver.get(current_issue_link)
time.sleep(10)
content2 = driver.page_source
current_issue_soup = BeautifulSoup(content2, 'html.parser')


print(current_issue_soup.prettify())

# Close the driver
driver.quit()
