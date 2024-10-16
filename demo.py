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
        # Look for <a> tags that might contain image links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Check if the URL belongs to the specified domain
            if urlparse(href).netloc.endswith(domain):
                urls.add(href)

        return urls

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
        file.write('<meta charset="UTF-8">\n')
        file.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
        file.write('<title>Image Gallery</title>\n')
        file.write('<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">\n')
        file.write('<link href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/css/lightbox.min.css" rel="stylesheet">\n')
        file.write('<style>.image-container { display: flex; justify-content: center; flex-wrap: wrap; }</style>\n')
        file.write('</head>\n')
        file.write('<body>\n')
        file.write('<div class="container">\n')
        file.write('<h1 class="text-center my-4">Extracted Images</h1>\n')
        file.write('<div class="row image-container">\n')
        
        count = 0
        for url in urls:
            if count >= max_images:
                break  # Stop adding images when the limit is reached

            file.write('<div class="col-md-3 mb-4">\n')
            file.write(f'<a href="{url}" data-lightbox="gallery" class="d-block">\n')
            file.write(f'<img src="{url}" class="img-fluid" alt="Image" style="border-radius: 10px;">\n')
            file.write('</a>\n')
            file.write('</div>\n')

            count += 1

        file.write('</div>\n')
        file.write(f'<h2 class="text-center">{count} images extracted</h2>\n')
        file.write('<center><button id="download-btn" class="btn btn-primary">Download All Images</button></center>\n')
        file.write('</div>\n')
        file.write('<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>\n')
        file.write('<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>\n')
        file.write('<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>\n')
        file.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/js/lightbox-plus-jquery.min.js"></script>\n')
        
        # Add JavaScript for downloading images
        file.write('''
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.7.1/jszip.min.js"></script>
        <script>
            document.getElementById("download-btn").addEventListener("click", function() {
                const urls = [\n''')
        
        for url in urls:
            file.write(f'"{url}",\n')
        
        file.write('''                ];
                const zip = new JSZip();
                const folder = zip.folder("images");
                
                Promise.all(urls.map(url => {
                    return fetch(url)
                        .then(response => {
                            if (!response.ok) throw new Error('Network response was not ok');
                            return response.blob();
                        })
                        .then(blob => {
                            const filename = url.split('/').pop();
                            folder.file(filename, blob);
                        });
                })).then(() => {
                    return zip.generateAsync({type:"blob"});
                }).then(function(content) {
                    const a = document.createElement("a");
                    a.href = URL.createObjectURL(content);
                    a.download = "images.zip";
                    a.click();
                }).catch(function(err) {
                    console.error("Error creating ZIP:", err);
                });
            });
        </script>
        ''')

        file.write('</body>\n')
        file.write('</html>\n')

# Example usage
website_url = ""  # Replace with the URL you want to scrape
domain_filter = ""  # Domain to filter

# Extract URLs from the page
extracted_urls = extract_href_from_page(website_url, domain_filter)

# Output the URLs to an HTML file
output_file = "images.html"
output_to_html(extracted_urls, output_file, 100)

print(f"Extracted URLs have been written to {output_file}")
