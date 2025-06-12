import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def fetch_data_from_urls(urls, css_selector):
    """
    Fetch data from a specific position on each webpage.

    :param urls: List of URLs to scrape.
    :param css_selector: CSS selector to locate the desired data.
    :return: List of extracted data.
    """
    extracted_data = []
    chromedriver_path = 'chromedriver/chromedriver.exe'  # Assumes chromedriver is in PATH or current directory
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    log_lines = []
    for url in urls:
        log_lines.append(f"Requesting URL (with JS rendering): {url}")
        try:
            driver.get(url)
            time.sleep(3)  # Wait for JavaScript to load content; adjust as needed
            html = driver.page_source
            log_lines.append(f"Page loaded. Content length: {len(html)}")
            soup = BeautifulSoup(html, 'html.parser')

            # Extract data for 3 different selectors
            css_selector1 = "h3 a"  # Example: book title links
            css_selector2 = "p.price_color"  # Example: price
            css_selector3 = "p.instock.availability"  # Example: availability

            elements1 = soup.select(css_selector1)
            elements2 = soup.select(css_selector2)
            elements3 = soup.select(css_selector3)

            data1 = elements1[0].text.strip() if elements1 else "No data found for selector 1"
            data2 = elements2[0].text.strip() if elements2 else "No data found for selector 2"
            data3 = elements3[0].text.strip() if elements3 else "No data found for selector 3"

            log_lines.append(f"css_selector1 ('{css_selector1}') result: {data1}")
            log_lines.append(f"css_selector2 ('{css_selector2}') result: {data2}")
            log_lines.append(f"css_selector3 ('{css_selector3}') result: {data3}")

            extracted_data.append((url, data1, data2, data3))
        except Exception as e:
            log_lines.append(f"Error occurred while processing {url}: {str(e)}")
            extracted_data.append((url, f"Error: {str(e)}", "", ""))

    driver.quit()

    # Save logs to a file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'runlog_{timestamp}.txt')
    with open(log_file, 'w', encoding='utf-8') as f:
        for line in log_lines:
            f.write(line + '\n')
    print(f"Saved run log to {log_file}")

    return extracted_data

if __name__ == "__main__":
    # Read URLs from Files/urls.csv (expects header: pgm,url)
    import csv
    urls_file = os.path.join(os.path.dirname(__file__), 'Files', 'urls.csv')
    url_entries = []  # List of dicts with 'pgm' and 'url'
    with open(urls_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('url', '').strip()
            pgm = row.get('pgm', '').strip()
            if url:
                url_entries.append({'pgm': pgm, 'url': url})
    urls = [entry['url'] for entry in url_entries]

    # Fetch and display data for 3 selectors
    results = fetch_data_from_urls(urls, None)

    # Save results to CSV file, including pgm
    import csv
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    outs_dir = os.path.join(os.path.dirname(__file__), 'Files', 'outs')
    os.makedirs(outs_dir, exist_ok=True)
    csv_file = os.path.join(outs_dir, f'results_{timestamp}.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['pgm', 'url', 'res1', 'res2', 'res3'])
        for entry, (url, data1, data2, data3) in zip(url_entries, results):
            writer.writerow([entry['pgm'], url, data1, data2, data3])
    print(f"Results saved to {csv_file}")
