import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, parse_qs
import re
from concurrent.futures import ThreadPoolExecutor  # For parallel downloading

# Step 1: Save the webpage source as index.html
def save_page_source(url, filename="index.html"):
    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()

        # Save the page source as index.html
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"Page source saved to {filename}.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")

# Step 2: Extract image links from the saved HTML page
def extract_image_links_from_html(filename="index.html", max_images=10, min_width=0, min_height=0):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        
        # Find all anchor tags that contain image links
        a_tags = soup.find_all("a", href=re.compile(r"\.(jpg|jpeg|png|gif|bmp|webp)$", re.IGNORECASE))
        valid_images = []
        count = 0

        for a_tag in a_tags:
            if count >= max_images:
                break
            img_url = a_tag.get("href")
            if not img_url:
                continue

            # Handle relative URLs
            if img_url.startswith("//"):
                img_url = f"http:{img_url}"
            elif img_url.startswith("/"):
                img_url = f"{url.rstrip('/')}{img_url}"

            valid_images.append(img_url)
            count += 1

        return valid_images
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

# Step 3: Save the image links to an HTML file (images.html)
def save_images_to_html(image_links, output_file="images.html"):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            # Write basic HTML structure with styling
            file.write(""" 
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Extracted Images</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f9;
                        margin: 0;
                        padding: 20px;
                    }
                    h1 {
                        text-align: center;
                        color: #333;
                    }
                    .gallery {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 15px;
                        justify-content: center;
                    }
                    .gallery img {
                        max-width: 200px;
                        max-height: 200px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }
                </style>
            </head>
            <body>
                <h1>Extracted Images</h1>
                <div class="gallery">
            """)
            # Add images
            for img_link in image_links:
                file.write(f'<img src="{img_link}" alt="Image">')
            file.write(""" 
                </div>
            </body>
            </html>
            """)
        print(f"Images saved to {output_file}.")
    except Exception as e:
        print(f"Error saving images to HTML: {e}")

# Step 4: Sanitize the filename
def sanitize_filename(img_url):
    """Sanitize the filename by extracting it from the URL query string."""
    
    # Check if the URL has a query string with 'f='
    parsed_url = urlsplit(img_url)
    query_params = parse_qs(parsed_url.query)
    
    # If there's a query parameter 'f', use it to extract the filename
    if 'f' in query_params:
        filename = query_params['f'][0]  # Get the filename from the 'f' parameter
    else:
        # Fallback to the base name from the URL path if 'f' is not present
        filename = os.path.basename(parsed_url.path)

    # Print to check the filename before sanitization
    print(f"Base filename before sanitization: {filename}")

    # Remove '%20' (space encoding) completely
    filename = filename.replace('%20', '')  # Remove '%20' (spaces)

    # Optionally, sanitize any other unwanted characters (e.g., invalid filesystem characters)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    print(f"Sanitized filename after removing invalid characters: {filename}")
    
    return filename

# Step 5: Download image
def download_image(img_url, download_folder="downloaded_images"):
    """Download image from the URL and save it to the specified folder."""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    try:
        print(f"Downloading {img_url}...")

        # Add headers to simulate a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        img_response = requests.get(img_url, headers=headers)
        img_response.raise_for_status()

        # Check if the response content type is an image
        content_type = img_response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            print(f"Skipping {img_url} (not an image).")
            return

        # Get the sanitized image filename
        img_name = sanitize_filename(img_url)  # Sanitize filename to keep the desired part
        img_path = os.path.join(download_folder, img_name)

        # Check if filename exists already, then add a number to avoid overwriting
        if os.path.exists(img_path):
            base_name, ext = os.path.splitext(img_name)
            counter = 1
            while os.path.exists(img_path):
                img_name = f"{base_name}_{counter}{ext}"
                img_path = os.path.join(download_folder, img_name)
                counter += 1

        # Save the image
        with open(img_path, "wb") as img_file:
            img_file.write(img_response.content)
        print(f"Saved {img_name} to {download_folder}.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {img_url}: {e}")

# Step 6: Ask user to download or skip the image
def ask_user_to_download_image(img_url):
    """Ask the user whether to download the image or not"""
    response = input(f"Do you want to download this image? {img_url} (1 for yes, 2 for no): ").strip()
    
    if response == "1":
        return img_url  # Return the image URL to be downloaded
    elif response == "2":
        print(f"Skipping image: {img_url}")
        return None
    else:
        print("Invalid input. Please enter '1' for yes or '2' for no.")
        return ask_user_to_download_image(img_url)

# Step 7: Download selected images concurrently
def download_images_concurrently(selected_images, download_folder="downloaded_images"):
    """Download multiple images concurrently."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Map download_image function to each image URL
        executor.map(lambda img_url: download_image(img_url, download_folder), selected_images)

# Main code to execute the steps
if __name__ == "__main__":
    # Hardcoded website URL
    website_url = " "  # Replace with your desired URL

    # Customizable parameters
    max_images = 0  # Maximum number of images to extract
    min_width = 0   # Minimum width of images (in pixels)
    min_height = 0  # Minimum height of images (in pixels)

    # Step 1: Save the webpage source as index.html
    save_page_source(website_url)

    # Step 2: Extract image links from the saved index.html
    image_links = extract_image_links_from_html("index.html", max_images, min_width, min_height)

    # Step 3: Save the extracted images to images.html
    save_images_to_html(image_links)

    # Step 4: Ask the user for each image whether to download it or not
    selected_images = []
    for img_url in image_links:
        selected_image = ask_user_to_download_image(img_url)
        if selected_image:
            selected_images.append(selected_image)

    # Step 5: Download the selected images concurrently
    download_images_concurrently(selected_images)

    print("Script finished.")
