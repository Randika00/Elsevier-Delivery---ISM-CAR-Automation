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
        site_key='6LfoPLQZAAAAAJeiXrDx2rycUOCbQ3fWpdNQnvPv',
        page_url=url)
    return result

def post_page(url):

    result = web_slover(url)
    payload = {'userCaptchaResponse': result}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    response = requests.post(url, data=payload, headers=headers)

    return response