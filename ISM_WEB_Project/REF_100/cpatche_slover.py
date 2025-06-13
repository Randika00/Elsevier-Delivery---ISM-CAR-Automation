import random
import time

from twocaptcha import TwoCaptcha
import requests


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}


def read_key_from_file(file_path):
    with open(file_path, 'r') as file:
        key = file.read().strip()
    return key

api_key = read_key_from_file('captcha_api.txt')
solver = TwoCaptcha(api_key)

def web_slover(url):

    result = solver.solve_captcha(
        site_key='6LcrtosaAAAAADRnMjagCVGiuXgoXFWysds7VKsG',
        page_url=url)
    time.sleep(random.uniform(1, 3))
    return result

def post_page(url):

    result = web_slover(url)
    payload = {'userCaptchaResponse': result}
    # headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    #     'Accept-Language': 'en-US,en;q=0.9,da;q=0.8',
    #     # 'Cache-Control': 'no-cache',
    #     'Connection': 'keep-alive',
    #     'Host': 'journals.biologists.com',
    #     # 'Pragma': 'no-cache',
    #     'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    #     'Sec-Ch-Ua-Mobile': '?0',
    #     'Sec-Ch-Ua-Platform': '"Windows"',
    #     'Sec-Fetch-Dest': 'document',
    #     'Sec-Fetch-Mode': 'navigate',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'Sec-Fetch-User': '?1',
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    # }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        # "Cookie": "American_Occupational_Therapy_AssociationMachineID=638465226214394544; _ga=GA1.3.913198106.1710925824; hubspotutk=45c7ea6f7f9bc84af981be5458cbd84f; _gcl_au=1.1.585721882.1710925826; _ga=GA1.1.913198106.1710925824; fpestid=4kF3LjnaKNrsHvB8tW4_YKTLTPNsD6vCuAlY0WCMKU5aAwe6XWWv6UtXpHzRbXLsSv41wA; _fbp=fb.1.1710925826667.1584579234; sa-user-id=s%253A0-e2678d88-10ca-5085-6e7f-9699543ec39e.aIOhjYU93e7TrKIeWR6gMMmTxJ02LKzL9HBy03tu1O8; sa-user-id-v2=s%253A4meNiBDKUIVuf5aZVD7DnsD4CYs.VtEorakjnt%252FJQzeCUbY79ctfGiblf2HOIqPboSWhdv8; sa-user-id-v3=s%253AAQAKIDXsHk-nPieIBwxcewSN2DK_yU_oPgQnkfXYHwGkT2yaEAEYAyCIiJCuBjABOgQhyhL0QgRXNvD_.c4W0g0ObZSPQuXL6BfKED0nlq%252BmsAqIVpcRJoitHQOc; visid_incap_531175=Zy2nzuSmR5yFKFg6O/LRzFEC/GUAAAAAQUIPAAAAAAAwq1h6OkWoDAVnjInquuek; _cc_id=887b3cc2fb5997a3d7d85844831d28a; __hstc=204606671.45c7ea6f7f9bc84af981be5458cbd84f.1710925825505.1711082917723.1711361540563.7; _clck=1vryupj%7C2%7Cfkd%7C0%7C1540; _ga_G5TCNFJCYP=GS1.1.1711361713.5.1.1711361955.0.0.0; _uetvid=b08cc970e69911ee91acfbf279c55fdb; _ga_3CVRFYYS90=GS1.1.1711364160.9.0.1711364160.60.0.0; TheDonBot=2D8CDC1F54EEADB0EC0E50BADDCA4B00; AJOT2_SessionId=b3bidki0pjbiwl4pfqrojvtv"

    }

    response = requests.post(url, data=payload, headers=headers,timeout=40)

    return response