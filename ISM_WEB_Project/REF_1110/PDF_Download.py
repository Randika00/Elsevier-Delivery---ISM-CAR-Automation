import requests

# Initial URL
initial_url = "https://portlandpress.com/clinsci/article-pdf/138/18/1179/961104/cs-2023-0681c.pdf"

# Create a session to handle the request
session = requests.Session()

# Step 1: Get the page content
response = session.get(initial_url)

# Check if the initial request was successful
if response.status_code == 200:
    # Step 2: Extract the final PDF download URL from the headers or content
    final_url = response.url  # This may contain the final redirect URL

    # Step 3: Download the actual PDF from the final URL
    pdf_response = session.get(final_url)

    # Check if the PDF was downloaded successfully
    if pdf_response.status_code == 200:
        # Save the PDF to a file
        with open("downloaded_file.pdf", "wb") as pdf_file:
            pdf_file.write(pdf_response.content)
        print("PDF downloaded successfully.")
    else:
        print(f"Failed to download PDF: {pdf_response.status_code}")
else:
    print(f"Failed to retrieve the initial page: {response.status_code}")
