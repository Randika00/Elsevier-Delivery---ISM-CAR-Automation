import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}


# url = "https://www.tjpr.org/admin/12389900798187/2024_23_9_1.pdf"
#
# session = requests.Session()
# session.headers.update(headers)
# response = session.get(url, headers=headers, stream=True)
# print(response)
# if response.status_code == 200:
#     with open('downloaded_pdf.pdf', 'wb') as f:
#         f.write(response.content)
#         print("PDF downloaded successfully!")

import requests

# Create a session
session = requests.Session()

# Specify the URL
url = "http://www.hjkxyj.org.cn/en/article/current"

# Set headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

# Send a GET request to the URL using the session with headers
response = session.get(url, headers=headers)

# Check the status code
if response.status_code == 200:
    print("Successfully retrieved the HTML content!")
    html_content = response.text
    print(html_content)
else:
    print(f"Failed to retrieve content. Status code: {response.status_code}")

