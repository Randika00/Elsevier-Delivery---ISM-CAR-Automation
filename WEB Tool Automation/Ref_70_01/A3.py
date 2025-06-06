import requests
from bs4 import BeautifulSoup

url = "https://revistas.unav.edu/index.php/anuario-filosofico/issue/archive"
response = requests.get(url)

current_link = next(
    (a.get('href') for a in BeautifulSoup(response.content, "html.parser").find("ul", id="main-navigation").find_all("a") if "Último número" in a.get_text()),
    None
)

print(current_link)

