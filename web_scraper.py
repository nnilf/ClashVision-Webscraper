import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from utils import filter_images_for_level, remove_duplicate_images, get_max_level
from image_and_data_handler import download_image_and_data
from parse_damage_table import get_building_stats
from error_handler import ErrorHandler
from Image_varities import find_image_varities

class WebScraper:

    def __init__(self, item_df, error_handler):
        # intialise df variables
        self._data_image_key = item_df["data-image-key"]
        self._WIKI_URL = item_df["URL"]
        self.levels = 0
        self._regex = ""
        self.error_handler = error_handler

        # create directory string for directory path to be created
        self._BASE_DIR = "items\\" + self._data_image_key

        # create directory path
        os.makedirs(self._BASE_DIR, exist_ok=True)

        # Headers to mimic a real browser request
        self._HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }


    def _fetch_item_images_and_data(self):
        """
        Fetches images of all levels of a particular building and filters it into levels.

        :return: A singular URL to the download_image function for it to be downloaded and saved to the directory
        """
        response = requests.get(self._WIKI_URL, headers=self._HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        df_path =  os.path.join(self._BASE_DIR, f"{self._data_image_key}_data.csv")

        if os.path.isfile(df_path):
            print(f"✅ Skipped {self._data_image_key} data, due to it already existing")
            df = pd.read_csv(df_path)
            self.levels = get_max_level(df)
        else:
            stats = get_building_stats(self._data_image_key, soup)
            for key in stats.keys():
                if key == "Main Stats":
                    df = stats[key]
                    self.levels = get_max_level(df)
                    df.to_csv(df_path, index=False)
                    print(f"✅ Saved: {df_path}")
                else:
                    key_text = key.replace(" ", "_")
                    df_path = os.path.join(self._BASE_DIR, f"{self._data_image_key}_{key_text}_data.csv")
                    df.to_csv(df_path, index=False)
                    print(f"✅ Saved: {df_path}")

        image_varities = find_image_varities(soup)

        for variety in image_varities:

            # set variety to current variety
            self._regex = variety

            # find all images for that particular variety
            gallery = soup.find_all("img", attrs={"data-image-key": re.compile(f"{self._data_image_key}\d+(-[1-5])?{self._regex}\.png")})

            if not(gallery):
                raise ValueError(f"Failed to find Images for '{self._data_image_key}'")

            for item in range(self.levels):
                item_level = item + 1

                # Find all images for item
                item_images_filtered = filter_images_for_level(gallery, item_level, self._data_image_key, self._regex)

                item_images_filtered = remove_duplicate_images(item_images_filtered)

                # check filtered items list isn't empty
                if not(item_images_filtered):
                    self.error_handler.add_error(f"Filtered list is empty for '{self._data_image_key}' level {item_level}")

                item_num = 1

                for figure in item_images_filtered:

                    # create path for checking whether image exists
                    path_join = os.path.join(self._BASE_DIR,f"{self._data_image_key}_{self._regex}", f"{self._data_image_key}_{item_level}_{item_num}{self._regex}.png")

                    # check whether image already exists
                    if os.path.isfile(path_join):
                        print(f"✅ Skipped {self._data_image_key}_{item_level}_{item_num}{self._regex} due to the image already existing")
                        # increment item number and then skip over item
                        item_num += 1
                        continue

                    if figure and "data-src" in figure.attrs:
                        img_url = figure["data-src"]
                        
                        img_url = img_url.split("/revision")[0]  # Remove unnecessary URL parts

                        download_image_and_data(img_url, item_level, item_num, self._BASE_DIR, self._data_image_key, self._regex)

                    item_num += 1
            

def scrape_item_images(item_df: pd.DataFrame):
    """
    Executes the higher level function of web scraping and downloads

    :param item_df: df of all the items in which web scraping needs to be applied on,
    containing: URL, data-image-key and levels
    :returns: Directory saved with all images of items from item_df
    """
    for index, row in item_df.iterrows():
        error_handler = ErrorHandler()

        web_scraper = WebScraper(row, error_handler)

        print(f"🔎 Fetching and downloading {web_scraper._data_image_key}{web_scraper._regex} images...")
        web_scraper._fetch_item_images_and_data()

    error_handler.save_errors()
    print(f"✅ All defensive building images downloaded successfully!")
    