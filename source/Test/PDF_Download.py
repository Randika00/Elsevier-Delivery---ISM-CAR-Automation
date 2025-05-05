import requests

# URL of the PDF file
url = "https://www.biother.cn/zgzlswzlzz/article/pdf/20241001"

# Define headers with a user-agent
headers = {
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "Accept-Encoding": "gzip, deflate",
    # "Accept-Language": "en-US,en;q=0.9",
    # "Connection": "keep-alive",
    # "Cookie": "FW9uCWqlVzC22m1KfCMCjfvFHpRMsgt=16c2a3a7-ee8d-4758-98cb-8116f2f95829; dGg2aCfMMK97Ro270mqBFu5qjC8TQbL2opnHvbEpM=jHgHRXGxQqlqnNnoAz2N8zh%2BsSOpvewHshCQCKNboPc%3D; dGg2aCfMMK97Ro270mqBFu5qjC8TQbL2opnHvbEpM=jHgHRXGxQqlqnNnoAz2N8zh%2BsSOpvewHshCQCKNboPc%3D; FW9uCWqlVzC22m1KfCMCjfvFHpRMsgt=16c2a3a7-ee8d-4758-98cb-8116f2f95829",
    # "Host": "www.dwjs.com.cn",
    # "Referer": "http://www.dwjs.com.cn/Qrj7QwVEvlj0ugWb%2B7cqdQzS7u%2BpFsXq69PXr0K%2BruIBa7%2BcYYgQd4IhCat3GaBl?encrypt=1",
    # "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}

# Send a GET request to the URL with headers
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print(response.status_code)
    # Open a file in binary write mode and write the response content
    with open('downloaded_file1.pdf', 'wb') as file:
        file.write(response.content)
    print("PDF file downloaded successfully!")
else:
    print(f"Failed to download PDF file. Status code: {response.status_code}")
