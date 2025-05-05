import requests
import time
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

api_key = "a03589ed562de14589af1d772c2b41bb"

url='https://research.aota.org/ajot/article/78/1/7801205040/25043/Use-of-the-Weekly-Calendar-Planning-Activity-to'

response = requests.get(url,headers=headers)
response_code = response.status_code
main_soup = BeautifulSoup(response.content, 'html.parser')

data_site_key = main_soup.find("div", {"id": "captcha"})["data-captchakey"]
request_url = "http://2captcha.com/in.php?key=" + str(api_key) + "&method=userrecaptcha&googlekey=" + str(data_site_key) + "&pageurl=" + url + ""
page = requests.get(request_url)
ok_key = str(page.text).replace("OK|", "")
print("resolving captcha key..")
respond_url = "http://2captcha.com/res.php?key=" + str(api_key) + "&action=get&id=" + str(ok_key) + ""

time.sleep(15)
page = requests.get(respond_url).text
while str(page).__contains__("CAPCHA_NOT_READY"):
    print("captcha still not ready..")
    time.sleep(10)
    page = requests.get(respond_url).text
code = str(page).replace("OK|", "")
time.sleep(2)

data = {
    "g-recaptcha-response": code,
}

response = requests.post(url, data=data,headers=headers)
print(response.text)
soup3 = BeautifulSoup(response.content, "lxml")
print(soup3)