from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
from PIL import Image
from io import BytesIO

def extract_href_from_page(url, domain):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    urls = set()
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        for a_tag in soup.find_all('a', class_='link link--external', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)  # Resolve relative URLs
            if urlparse(full_url).netloc.endswith(domain):
                urls.add(full_url)
        
        print(f"Extracted {len(urls)} URLs from {url}")
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
    finally:
        driver.quit()
    
    return urls

def is_valid_image(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for request errors
        
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        file_format = img.format.lower()
        
        # Check file format and dimensions
        if file_format in ['jpeg', 'jpg', 'png'] and width > 900 and height > 900:
            return True
    except Exception as e:
        # print(f"An error occurred while checking image {url}: {e}")
        print(f"An error occurred while checking image")
    
    return False

def extract_image_urls_from_page(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    image_urls = set()
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src']
            full_url = urljoin(url, src)  # Resolve relative URLs
            if is_valid_image(full_url):
                image_urls.add(full_url)
        
        print(f"Extracted {len(image_urls)} valid image URLs from {url}")
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
    finally:
        driver.quit()
    
    return image_urls

def output_to_html(urls, output_file, max_images):
    with open(output_file, 'w') as file:

        file.write('<!DOCTYPE html>\n')
        file.write('<html lang="en">\n')

        file.write('<head>\n')
        file.write('<meta charset="UTF-8">\n')
        file.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
        file.write('<title>Image Gallery</title>\n')
        file.write('<link href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/css/lightbox.min.css" rel="stylesheet">\n')
        file.write('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">\n')
        file.write('<style>.image-container {display: flex;justify-content: center;flex-wrap: wrap;margin-top: 20px;}.card img {object-fit: cover;}.checkbox-wrapper {text-align: center;margin-top: 10px;}</style>\n')
        file.write('</head>\n')

        file.write('<body>\n')

        file.write('<main class="container">\n')
        file.write('<div class="row image-container">\n')

        count = 0
        for url in urls:
            if count >= max_images:
                break

            file.write('<div class="col-md-3 mt-4">\n')
            file.write('<div class="card" style="width: 18rem;">\n')
            file.write(f'<a href="{url}" data-lightbox="image-gallery" data-title="Iamge {count}">\n')
            file.write(f'<img src="{url}" class="card-img-top" alt="" width="150px" height="150px">\n')
            file.write('</a>\n')
            file.write('<div class="checkbox-wrapper">\n')
            file.write(f'<input type="checkbox" class="image-checkbox" data-src="{url}" checked> Select\n')
            file.write('</div>\n')
            file.write('</div>\n')
            file.write('</div>\n')

            count += 1

        file.write('</div>\n')
        file.write(f'<center><button id="download-btn" class="mt-5 mb-5 btn btn-primary font-weight-bold">Download {count}</button></center>\n')
        file.write('</main>\n')

        file.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/js/lightbox-plus-jquery.min.js"></script>\n')
        file.write('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy" crossorigin="anonymous"></script>\n')
        file.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.7.1/jszip.min.js"></script>\n')
        file.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip-utils/0.1.0/jszip-utils.min.js"></script>\n')

        file.write('<script src="js/func-zip.js"></script>\n')

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
    website_url = ""  # Change this to the target website
    domain_filter = ""  # Domain to filter
    increase_scale = 0  # Add image count
    
    # Initial extraction
    extracted_urls = extract_href_from_page(website_url, domain_filter)
    
    # Output the initial URLs to an HTML file
    output_file = "images.html"
    output_to_html(extracted_urls, output_file, increase_scale)  # Set max_images to 2 for initial output

    print(f"Initial extraction complete. Output written to {output_file}")

    # Read URLs from the HTML file and extract valid image data from each URL
    urls_from_html = extract_urls_from_html(output_file)
    
    all_image_urls = set()
    for url in urls_from_html:
        if not urlparse(url).scheme:  # Skip URLs without a scheme
            continue
        print(f"Processing URL: {url}")
        image_urls = extract_image_urls_from_page(url)
        all_image_urls.update(image_urls)
        print(f"Found {len(image_urls)} valid image URLs from {url}")

    # Output the combined extracted image URLs to a new HTML file
    final_output_file = "combined_images.html"
    output_to_html(all_image_urls, final_output_file, increase_scale)  # Set max_images to 2 for final output

    print(f"Combined extraction complete. Output written to {final_output_file}")

if __name__ == "__main__":
    main()
