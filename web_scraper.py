import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
import re

class WebScraper:

    def __init__(self, item_df):
        # intialise df variables
        self._data_image_key = item_df["data-image-key"][0]
        self._URL = item_df["URL"][0]
        self._levels = item_df["levels"][0]

        self._BASE_DIR = self._data_image_key

        os.makedirs(self._BASE_DIR, exist_ok=True)

        # URL of the wiki page
        self._WIKI_URL = item_df["URL"][0]

        # Headers to mimic a real browser request
        self._HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _filter_images(self, img_elements, level):
        """Filters <img> elements to only include those with a matching data-image-key."""
        pattern = re.compile(f"{self._data_image_key}{level}(-[1-5])?\.png")

        return [
            img for img in img_elements 
            if img.has_attr("data-image-key") and pattern.match(img["data-image-key"])
        ]

    # Function to scrape item images
    def _fetch_item_images(self):
        response = requests.get(self._WIKI_URL, headers=self._HEADERS)
        if response.status_code != 200:
            print("Failed to fetch the Wiki page.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        item_images = [[] for i in range(17)]
    
        gallery = soup.find_all("img", attrs={"data-image-key": re.compile(f"{self._data_image_key}\d+(-[1-5])?\.png")})

        for item in range(self._levels):
            item_level = item + 1
            # Find all images for item
            item_images_filtered = self._filter_images(gallery, item_level)

            for figure in item_images_filtered:
                if figure and "data-src" in figure.attrs:
                    img_url = figure["data-src"]
                    
                    # Some images have low-resolution links; fetch the higher-quality version
                    img_url = img_url.split("/revision")[0]  # Remove unnecessary URL parts
                    
                    item_images[item].append(img_url)

        return item_images

    # Function to download images and save them in folders
    def _download_images(self, item_images):
        level = 1
        for item in item_images:
            folder_path = os.path.join(self._BASE_DIR, f"{self._data_image_key}_{level}")
            os.makedirs(folder_path, exist_ok=True)

            for images in range(len(item)):
                try:
                    response = requests.get(item[images], stream=True)
                    response.raise_for_status()

                    image = Image.open(BytesIO(response.content))
                    image_format = image.format.lower()
                    image_path = os.path.join(folder_path, f"{self._data_image_key}_{level}_{images+1}.{image_format}")

                    image.save(image_path)
                    print(f"✅ Saved: {image_path}")

                    time.sleep(1)  # Avoid hitting the server too fast
                except Exception as e:
                    print(f"❌ Failed to download {self._data_image_key}{level} image: {e}")
            
            level += 1

# Main execution
def execution(item_df: pd.DataFrame):
    web_scraper = WebScraper(item_df)

    print("🔎 Fetching item images...")
    item_images = web_scraper._fetch_item_images()

    if item_images:
        print("📥 Downloading images...")
        web_scraper._download_images(item_images)
        print("✅ All item images downloaded successfully!")
    else:
        print("❌ No images found!")
    