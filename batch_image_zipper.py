import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
from tqdm import tqdm  # Import tqdm for progress bar

def process_images():
    # Step 1: Parse combined_images.html
    html_file = "combined_images.html"
    download_folder = "downloaded_images"
    zip_file_name = "images.zip"

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Read the HTML file
    with open(html_file, "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Extract image URLs
    img_tags = soup.find_all("img")
    img_urls = [img["src"] for img in img_tags if "src" in img.attrs]

    print(f"Found {len(img_urls)} images.")

    # Step 2: Download the images with a progress bar
    downloaded_files = []
    print("Downloading images...")
    for idx, img_url in enumerate(tqdm(img_urls, desc="Downloading")):  # Add progress bar
        try:
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join(download_folder, f"image_{idx + 1}.jpg")
                with open(file_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
                downloaded_files.append(file_path)
            else:
                print(f"Failed to download: {img_url}")
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")

    print(f"Downloaded {len(downloaded_files)} images.")

    # Step 3: Zip the images
    print("Zipping images...")
    with ZipFile(zip_file_name, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, os.path.basename(file))
    print(f"Images zipped into {zip_file_name}")

    # Step 4: Corrupt the images by reducing them to 0 bytes
    print("Corrupting images...")
    for file_path in tqdm(downloaded_files, desc="Corrupting"):  # Add progress bar for corrupting
        try:
            with open(file_path, "wb") as empty_file:
                empty_file.truncate(0)  # Reduce file size to 0 bytes
        except Exception as e:
            print(f"Error corrupting {file_path}: {e}")

    # Step 5: Wait for user input to delete corrupted images
    user_input = input("Do you want to delete the corrupted images? (y/n): ").strip().lower()
    if user_input == "y":
        for file_path in downloaded_files:
            os.remove(file_path)
        print("Corrupted images deleted.")
    else:
        print("Corrupted images retained.")

if __name__ == "__main__":
    process_images()
