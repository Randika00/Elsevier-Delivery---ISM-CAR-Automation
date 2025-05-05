import requests
from bs4 import BeautifulSoup


def get_soup(url):
    # Replace with your actual API key from ScraperAPI
    api_key = "7d49f35401add80a972bbc292a3016a3"
    curl = f"http://api.scraperapi.com?api_key={api_key}&url={url}"

    # Send the request using ScraperAPI, which handles JavaScript rendering
    response = requests.get(curl)
    response_code = response.status_code
    if response_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup, response_code
    else:
        return None, response_code


url = "http://www.hjkxyj.org.cn/en/article/current"
soup, response_code = get_soup(url)

if soup:
    print(soup.prettify())
else:
    print(f"Failed to retrieve content, status code: {response_code}")
