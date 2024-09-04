from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_href_from_page(url, domain):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        urls = set()
        for a_tag in soup.find_all('a', class_='link link--external', href=True):
            href = a_tag['href']
            if urlparse(href).netloc.endswith(domain):
                urls.add(href)
        
        print(f"Extracted {len(urls)} URLs from {url}")
        return urls

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
        return set()
    finally:
        driver.quit()

def output_to_html(urls, output_file, max_images):
    with open(output_file, 'w') as file:
        file.write('<!DOCTYPE html>\n')
        file.write('<html lang="en">\n')
        file.write('<head>\n')
        file.write('<link href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/css/lightbox.min.css" rel="stylesheet">\n')
        file.write('</head>\n')
        file.write('<body>\n')
        file.write('<center>\n')
        
        count = 0
        for url in urls:
            if count >= max_images:
                break

            file.write(f'<a href="{url}" target="_blank" class="link link--external">\n')
            file.write(f'<img src="{url}" width="150px" height="150px" alt="Image">\n')

            count += 1

        file.write('</center>\n')
        file.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/js/lightbox-plus-jquery.min.js"></script>\n')
        file.write('</body>\n')
        file.write('</html>\n')

def extract_urls_from_html(html_file):
    urls = set()
    try:
        with open(html_file, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if href:  # Check if href is not empty
                    urls.add(href)
    except Exception as e:
        print(f"An error occurred while reading {html_file}: {e}")
    print(f"Extracted {len(urls)} URLs from {html_file}")
    return urls

def main():
    website_url = ""  # Change this if needed
    domain_filter = ""  # Domain to filter
    
    # Initial extraction
    extracted_urls = extract_href_from_page(website_url, domain_filter)
    
    # Output the initial URLs to an HTML file
    output_file = "images.html"
    output_to_html(extracted_urls, output_file, 1)

    print(f"Initial extraction complete. Output written to {output_file}")

    # Read URLs from the HTML file and extract data from each URL
    urls_from_html = extract_urls_from_html(output_file)
    
    all_extracted_urls = set()
    for url in urls_from_html:
        if not urlparse(url).scheme:  # Handle relative URLs
            continue
        print(f"Processing URL: {url}")
        new_urls = extract_href_from_page(url, domain_filter)
        all_extracted_urls.update(new_urls)
        print(f"Found {len(new_urls)} new URLs from {url}")

    # Output the combined extracted URLs to a new HTML file
    final_output_file = "combined_images.html"
    output_to_html(all_extracted_urls, final_output_file, 1)

    print(f"Combined extraction complete. Output written to {final_output_file}")

if __name__ == "__main__":
    main()
