import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

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

            # Collect all selectors (tag, class, id) from the response
            selectors = set()
            for tag in soup.find_all(True):
                if tag.name:
                    selectors.add(tag.name)
                if tag.get('class'):
                    for cls in tag.get('class'):
                        selectors.add(f".{cls}")
                if tag.get('id'):
                    selectors.add(f"#{tag.get('id')}")

            # Save selectors to a file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'selectors_{timestamp}.txt')
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write("Selectors found (grouped):\n")
                tag_selectors = sorted([s for s in selectors if not s.startswith('.') and not s.startswith('#')])
                class_selectors = sorted([s for s in selectors if s.startswith('.')])
                id_selectors = sorted([s for s in selectors if s.startswith('#')])

                f.write("  Tags:\n")
                for selector in tag_selectors:
                    f.write(f"    {selector}\n")
                f.write("  Classes:\n")
                for selector in class_selectors:
                    f.write(f"    {selector}\n")
                f.write("  IDs:\n")
                for selector in id_selectors:
                    f.write(f"    {selector}\n")
            print(f"Saved selectors to {log_file}")

            elements = soup.select(css_selector)
            print(f"Found {len(elements)} elements with selector '{css_selector}'")
            if elements:
                print(f"First element text: {elements[0].text.strip()}")
                extracted_data.append((url, elements[0].text.strip()))
            else:
                print("No element found on this page.")
                extracted_data.append((url, "No data found at the specified position"))
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
