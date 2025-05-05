from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Set up headless Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")

# Automatically install the appropriate version of ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL to load
url = "https://xuebaozr.sysu.edu.cn/homeNav?lang=en"

# Load the webpage
driver.get(url)

# Get the rendered HTML content
html_content = driver.page_source

# Print or parse the HTML content
print(html_content)

# Quit the browser after use
driver.quit()
