import requests
from bs4 import BeautifulSoup

def fetch_data_from_urls(urls, css_selector):
    """
    Fetch data from a specific position on each webpage.

    :param urls: List of URLs to scrape.
    :param css_selector: CSS selector to locate the desired data.
    :return: List of extracted data.
    """
    extracted_data = []
    for url in urls:
        print(f"Requesting URL: {url}")
        try:
            response = requests.get(url)
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                print(f"Page loaded successfully. Content length: {len(response.text)}")
            else:
                print(f"Warning: Received status code {response.status_code}")
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.select(css_selector)
            print(f"Found {len(elements)} elements with selector '{css_selector}'")
            if len(elements) >= 2:
                print(f"Second element text: {elements[1].text.strip()}")
                extracted_data.append((url, elements[1].text.strip()))
            else:
                print("Second book not found on this page.")
                extracted_data.append((url, "Second book not found"))
        except Exception as e:
            print(f"Error occurred while processing {url}: {str(e)}")
            extracted_data.append((url, f"Error: {str(e)}"))
    return extracted_data

if __name__ == "__main__":
    # Example list of URLs
    urls = [
        "http://books.toscrape.com/catalogue/page-1.html",
        # Add more URLs here
    ]

    # CSS selector for the desired position (update as needed)
    css_selector = "article.product_pod h3 a"  # Selector for the first book's name

    # Fetch and display data
    results = fetch_data_from_urls(urls, css_selector)
    for url, data in results:
        print(f"URL: {url}\nData: {data}\n")
