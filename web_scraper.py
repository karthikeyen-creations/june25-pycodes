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
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.select(css_selector)
            if len(elements) >= 2:
                extracted_data.append((url, elements[1].text.strip()))
            else:
                extracted_data.append((url, "Second book not found"))
        except Exception as e:
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
