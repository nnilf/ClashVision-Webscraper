import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
import re
from bs4 import Tag

class WebScraper:

    def __init__(self, item_df):
        # intialise df variables
        self._data_image_key = item_df["data-image-key"]
        self._WIKI_URL = item_df["URL"]
        self._levels = item_df["levels"]

        # create directory string for directory path to be created
        self._BASE_DIR = "items\\" + self._data_image_key

        # create directory path
        os.makedirs(self._BASE_DIR, exist_ok=True)

        # Headers to mimic a real browser request
        self._HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }


    def _remove_duplicate_images(self, img_elements):
        """
        Removes duplicate image elements based on their 'data-src' attribute using regex masks.

        :param img_elements: List of image elements.
        :return: List of unique image elements.
        """
        unique_imgs = list({img['data-image-key'].strip(): img for img in img_elements if isinstance(img, Tag) and img.has_attr('data-image-key')}.values())

        return unique_imgs
    

    def _filter_images(self, img_elements, level):
        """
        Filters <img> elements to only include those images from that particular building level.

        :param img_elements: List of image elements.
        :param level: Level that is wanted to be retrieved.
        :return: List of image elements that match that particular level.
        """
        pattern = re.compile(f"{self._data_image_key}{level}(-[1-5])?\.png")

        return [
            img for img in img_elements 
            if img.has_attr("data-image-key") and pattern.match(img["data-image-key"])
        ]


    def _fetch_item_images(self):
        """
        Fetches images of all levels of a particular building.

        :return: List of URLs for the images that needed to be downloaded and stored.
        """
        response = requests.get(self._WIKI_URL, headers=self._HEADERS)
        if response.status_code != 200:
            print("Failed to fetch the Wiki page.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        item_images = [[] for i in range(self._levels)]
    
        gallery = soup.find_all("img", attrs={"data-image-key": re.compile(f"{self._data_image_key}\d+(-[1-5])?\.png")})

        for item in range(self._levels):
            item_level = item + 1
            # Find all images for item
            item_images_filtered = self._filter_images(gallery, item_level)

            item_images_filtered = self._remove_duplicate_images(item_images_filtered)

            for figure in item_images_filtered:
                if figure and "data-src" in figure.attrs:
                    img_url = figure["data-src"]
                    
                    img_url = img_url.split("/revision")[0]  # Remove unnecessary URL parts
                    
                    item_images[item].append(img_url)

        return item_images


    def _download_images(self, item_images):
        """
        Downloads images from provided list of URLs.

        :param item_images: List of URLs for the function to download and store .
        :return: Downloads all images to given file directory, stored in seperate levels.
        """
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


def scrape_item_images(item_df: pd.DataFrame):
    """
    Executes the higher level connection of web scraping functions

    :param item_df: df of all the items in which web scraping needs to be applied on,
    containing: URL, data-image-key and levels
    :returns: Directory saved with all images of items from item_df
    """
    for index, row in item_df.iterrows():
        web_scraper = WebScraper(row)

        print(f"🔎 Fetching {web_scraper._data_image_key} images...")
        item_images = web_scraper._fetch_item_images()

        if item_images:
            print("📥 Downloading images...")
            web_scraper._download_images(item_images)
            print(f"✅ All {web_scraper._data_image_key} images downloaded successfully!")
        else:
            print(f"❌ No {web_scraper._data_image_key} found!")

    print(f"✅ All defensive building images downloaded successfully!")
    