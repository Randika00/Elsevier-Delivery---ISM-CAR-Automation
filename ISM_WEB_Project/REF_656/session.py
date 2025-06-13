import requests
from bs4 import BeautifulSoup


def get_soup(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


# Create a session object to persist cookies and headers across requests
session = requests.session()

# URLs for login and user page
url = "http://www.eemj.eu/index.php/EEMJ"
login_link = 'https://www.eemj.eu/index.php/EEMJ/login/signIn'
user_link = 'https://www.eemj.eu/index.php/EEMJ/user'

# Headers to simulate a browser
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "connection": "keep-alive",
    "cookie": "OJSSID=g3t0heor3trco128jbv3snkld4",
    "host": "www.eemj.eu",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# Step 1: Get the initial login page to fetch cookies and session data
session.get(url, headers=headers)

# Step 2: Prepare the login payload (credentials)
payload = {
    "username": "full_access",  # Replace with your actual username
    "password": "13243546"  # Replace with your actual password
}

header_data = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "content-length": "38",
    "content-type": "application/x-www-form-urlencoded",
    "cookie": "OJSSID=ojt5706usrj77231mbm2e0f6d4",
    "origin": "https://www.eemj.eu",
    "priority": "u=0, i",
    "referer": "https://www.eemj.eu/index.php/EEMJ/login",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}


# Step 3: Perform the login POST request
login_response = session.post(login_link, headers=header_data, data=payload)

cookies_main = login_response.cookies
cookie_str = '; '.join([f"{cookie.name}={cookie.value}" for cookie in cookies_main])
header_login= {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": cookie_str,
    "priority": "u=0, i",
    "referer": "https://www.eemj.eu/index.php/EEMJ/login/signIn",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

headers4 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    #"cookie": "OJSSID=u0njn2p4cqrgrubhibmbea9on3",
    "priority": "u=0, i",
    "referer": "https://www.eemj.eu/index.php/EEMJ/issue/view/264",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

# Step 4: Check if the login was successful by inspecting the response status code
if login_response.status_code == 200:
    print("Login successful")

    # Step 5: Access the user page to verify session persistence
    user_page = session.get(user_link, headers=header_login)

    # Check if the user page was successfully loaded (meaning the session is valid)
    if user_page.status_code == 200:
        print("User page accessed successfully")

        # Fetch the current articles page
        res2 = session.get(url, headers=headers)
        soup = BeautifulSoup(res2.content, "html.parser")

        # Find the current link for the articles
        current_li = soup.find("li", id="current")
        if current_li:
            current_link = current_li.find("a").get('href')
            soup2 = get_soup(current_link, headers=headers)

            # Fetch all articles
            articles = soup2.find_all("table", class_="tocArticle")
            total_count = len(articles)
            print(f"Total number of articles: {total_count}\n")

            for article in articles:
                Article_link = article.find("div", class_="tocTitle").find('a').get('href')
                article_link = session.get(Article_link, headers=headers4)
                soup3 = BeautifulSoup(article_link.content, "html.parser")
                pdf_link=soup3.find("div",attrs={"id":"articleFullText"}).a["href"].replace("view","download")
                print("Article Link:", pdf_link)

        else:
            print("No 'current' link found on the page.")

    else:
        print("Failed to access user page.")
else:
    # Print response text for debugging
    print("Login failed. Check your credentials or request details.")
    print(login_response.text)
