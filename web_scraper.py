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

    import csv
    # Read selectors from Files/selectors.csv
    selectors_file = os.path.join(os.path.dirname(__file__), 'Files', 'selectors.csv')
    selectors = []
    with open(selectors_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            selectors.append(row['selector'])

    log_lines = []
    for url in urls:
        log_lines.append(f"Requesting URL (with JS rendering): {url}")
        try:
            driver.get(url)
            time.sleep(3)  # Wait for JavaScript to load content; adjust as needed
            html = driver.page_source
            log_lines.append(f"Page loaded. Content length: {len(html)}")
            soup = BeautifulSoup(html, 'html.parser')

            results = []
            for idx, selector in enumerate(selectors):
                elements = soup.select(selector)
                if elements:
                    data = elements[0].text.strip()
                else:
                    data = f"No data found for selector {idx+1}"
                log_lines.append(f"{selector} result: {data}")
                results.append(data)

            # Pad results to always have 3 columns
            while len(results) < 3:
                results.append("")
            extracted_data.append((url, results[0], results[1], results[2]))
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
            print(f"pgm: {entry['pgm']}")
            print(f"url: {url}")
            print(f"res1: {data1}")
            print(f"res2: {data2}")
            print(f"res3: {data3}\n")
    print(f"Results saved to {csv_file}")
