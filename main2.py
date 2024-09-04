from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_image_urls_from_page(url, domain):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        # Wait for content to load
        driver.implicitly_wait(10)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract image URLs
        image_elements = soup.find_all('img', src=True)
        
        image_urls = set()
        for img in image_elements:
            full_url = urljoin(url, img['src'])
            # Check if the URL belongs to the specified domain
            if urlparse(full_url).netloc.endswith(domain):
                image_urls.add(full_url)

        return image_urls

    except Exception as e:
        print(f"An error occurred: {e}")
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
                break  # Stop adding images when the limit is reached

            file.write(f'<a href="{url}" data-lightbox="image-gallery" data-title="Image">\n')
            file.write(f'<img src="{url}" width="150px" height="150px" alt="Image">\n')

            count += 1
        
        file.write('</center>\n')
        file.write(f'<center><h2>{count}</h2></center>\n')
        file.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/js/lightbox-plus-jquery.min.js"></script>\n')
        file.write('</body>\n')
        file.write('</html>\n')

# Example usage
website_url = ""  # Change this if needed
domain_filter = ""  # Domain to filter
extracted_urls = extract_image_urls_from_page(website_url, domain_filter)

# Output the URLs to an HTML file
output_file = "images.html"
output_to_html(extracted_urls, output_file, 100)

print(f"Extracted URLs have been written to {output_file}")
