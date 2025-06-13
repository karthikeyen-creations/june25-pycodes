import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_data_from_urls(urls, css_selector, out_dir=None):
    """
    Fetch data from a specific position on each webpage.

    :param urls: List of URLs to scrape.
    :param css_selector: CSS selector to locate the desired data.
    :param out_dir: Directory to save downloaded files.
    :return: List of extracted data.
    """
    extracted_data = []
    chromedriver_path = 'chromedriver/chromedriver.exe'  # Assumes chromedriver is in PATH or current directory
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    if out_dir:
        prefs = {"download.default_directory": out_dir,
                 "download.prompt_for_download": False,
                 "download.directory_upgrade": True,
                 "safebrowsing.enabled": True}
        chrome_options.add_experimental_option("prefs", prefs)
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    import csv
    # Read selectors from Files/selectors.csv
    selectors_file = os.path.join(os.path.dirname(__file__), 'Files', 'selectors.csv')
    selectors = []
    button_selector = None
    with open(selectors_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['selector_name'] == 'button_selector':
                button_selector = row['selector']
            else:
                selectors.append(row['selector'])

    log_lines = []
    for url in urls:
        log_lines.append(f"Requesting URL (with JS rendering): {url}")
        try:
            driver.get(url)
            time.sleep(3)  # Wait for JavaScript to load content; adjust as needed
            # Try to click the 'Add to basket' button if present, using button_selector from selectors.csv
            if button_selector:
                try:
                    # Wait for the button to be clickable
                    csv_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
                    )
                    csv_btn.click()
                    log_lines.append(f"Clicked button using selector: {button_selector}")
                    # Wait for possible download
                    time.sleep(3)
                    # Check for new files in the download directory
                    if out_dir:
                        downloaded_files = os.listdir(out_dir)
                        if downloaded_files:
                            log_lines.append(f"Downloaded files after clicking: {downloaded_files}")
                        else:
                            log_lines.append("No files detected in download folder after clicking.")
                except Exception as click_e:
                    log_lines.append(f"Button not found or not clickable with selector '{button_selector}': {click_e}")
            else:
                log_lines.append("No button_selector found in selectors.csv.")

            html = driver.page_source
            log_lines.append(f"Page loaded. Content length: {len(html)}")
            soup = BeautifulSoup(html, 'html.parser')

            # Log all selectors available on the page before clicking the button
            found_selectors = set()
            for tag in soup.find_all(True):
                if tag.name:
                    found_selectors.add(tag.name)
                if tag.get('class'):
                    for cls in tag.get('class'):
                        found_selectors.add(f'.{cls}')
                if tag.get('id'):
                    found_selectors.add(f'#{tag.get('id')}')
            log_lines.append(f"Selectors available before clicking: {sorted(found_selectors)}")

            results = []

            for idx, selector in enumerate(selectors):
                elements = soup.select(selector)
                if elements:
                    data = elements[0].text.strip()
                    # Replace non-breaking space (U+00a0) with ' | '
                    data = data.replace('\u00a0', ' | ')
                    # Convert multiline to single line with ' | '
                    if '\n' in data:
                        data = ' | '.join(line.strip() for line in data.splitlines() if line.strip())
                else:
                    data = f"No data found for selector {idx+1}"
                log_lines.append(f"{selector} result: {data}")
                results.append(data)

            # Pad results to always have 4 columns
            while len(results) < 4:
                results.append("")
            extracted_data.append((url, results[0], results[1], results[2], results[3]))
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

    # Create a timestamped output folder inside Files/outs
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    outs_base_dir = os.path.join(os.path.dirname(__file__), 'Files', 'outs')
    os.makedirs(outs_base_dir, exist_ok=True)
    out_dir = os.path.join(outs_base_dir, timestamp)
    os.makedirs(out_dir, exist_ok=True)

    # Fetch and display data for selectors, pass out_dir
    results = fetch_data_from_urls(urls, None, out_dir=out_dir)

    # Save results to CSV file, including pgm, in Files/outs (not timestamped folder)
    csv_file = os.path.join(outs_base_dir, f'results_{timestamp}.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['pgm', 'url', 'res1', 'res2', 'res3', 'res4'])
        for entry, (url, data1, data2, data3, data4) in zip(url_entries, results):
            writer.writerow([entry['pgm'], url, data1, data2, data3, data4])
            print(f"pgm: {entry['pgm']}")
            print(f"url: {url}")
            print(f"res1: {data1}")
            print(f"res2: {data2}")
            print(f"res3: {data3}")
            print(f"res4: {data4}\n")
    print(f"Results saved to {csv_file}")
