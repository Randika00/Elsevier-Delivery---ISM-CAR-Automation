from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time

# Instantiate the WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Load the target page
captcha_page_url = "https://onepetro.org/crawlprevention/governor?content=%2fDC%2fissue"
driver.get(captcha_page_url)

print("Solving Captcha")
solver = TwoCaptcha("a03589ed562de14589af1d772c2b41bb")
response = solver.recaptcha(sitekey='6LdPAeQUAAAAAG-CObu_TqhyW8Z_yPQL5uszzDAw', url=captcha_page_url)
code = response['code']
print(f"Successfully solved the Captcha. The solve code is {code}")

# Set the solved Captcha
recaptcha_response_element = driver.find_element(By.ID, 'g-recaptcha-response')
driver.execute_script(f'arguments[0].value = "{code}";', recaptcha_response_element)

# Submit the form
submit_btn = driver.find_element(By.ID, 'btnSubmit')
submit_btn.click()

# Pause the execution so you can see the screen after submission before closing the driver
input("Press enter to continue")
driver.close()