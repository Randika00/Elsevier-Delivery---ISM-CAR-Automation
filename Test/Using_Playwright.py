from playwright.sync_api import sync_playwright


def get_html_content():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=True)

        # Create a new browser context and page
        context = browser.new_context()
        page = context.new_page()

        # Specify the URL
        url = "http://www.dwjs.com.cn/zMl970eJZ4Ye0Q%2BZ69qbTw%3D%3D?encrypt=1"

        # Navigate to the URL
        page.goto(url)

        # Get the page content
        html_content = page.content()
        print(html_content)  # Print the HTML content or process it as needed

        # Close the browser
        browser.close()


# Call the function
get_html_content()