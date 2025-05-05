import captcha_main
url = "https://research.aota.org/ajot"


r = captcha_main.captcha_main(url)
print(r.status_code)
print(r.content)