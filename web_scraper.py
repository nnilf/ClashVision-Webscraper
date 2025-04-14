import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from utils import filter_images_for_level, remove_duplicate_images
from image_and_data_handler import download_image_and_data
from parse_damage_table import get_building_stats

class WebScraper:

    def __init__(self, item_df):
        # intialise df variables
        self._data_image_key = item_df["data-image-key"]
        self._WIKI_URL = item_df["URL"]
        self.levels = 0
        self._regex = item_df['regex']

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
        if response.status_code != 200:
            print("Failed to fetch the Wiki page.")
            return []
        
        archer_stats = get_building_stats("Archer_Tower")
        cannon_stats = get_building_stats("Cannon")
        mortar_stats = get_building_stats("Mortar")
        air_defense_stats = get_building_stats("Air_Defense")
        wizard_tower_stats = get_building_stats("Wizard_Tower")
        Air_Sweeper_stats = get_building_stats("Air_Sweeper")
        Hidden_Tesla_stats = get_building_stats("Hidden_Tesla")
        Bomb_Tower_stats = get_building_stats("Bomb_Tower")

        # Now you'll get properly named tables:
        print(archer_stats.keys()) 
        # Output: ['Home Village Stats', 'Fast Attack', 'Long Attack']

        soup = BeautifulSoup(response.text, "html.parser")
    
        gallery = soup.find_all("img", attrs={"data-image-key": re.compile(f"{self._data_image_key}\d+(-[1-5])?{self._regex}\.png")})
        tables = soup.find_all("table", class_="wikitable floatheader row-highlight")

        for table in tables:
            level = table.find_all("tr")[0].text.strip()[:5]
            if level == "Level":

                df_path =  os.path.join(self._BASE_DIR, f"{self._data_image_key}_data.csv")

                if os.path.isfile(df_path):
                    print(f"✅ Skipped {self._data_image_key} data, due to it already existing")
                    break

                else:
                    df = get_building_stats(table)
                    max_level = df["Level"][len(df)-1]
                    self.levels = int(max_level)
                    df.to_csv(df_path, index=False)
                    print(f"✅ Saved: {self._data_image_key} data")
                    break
        
        if not level:
            print(f'❌ Failed to find data table for {self._data_image_key}!')

        if not(gallery):
            print(f"❌ Failed to find {self._data_image_key}!")
            return

        for item in range(self.levels):
            item_level = item + 1

            # Find all images for item
            item_images_filtered = filter_images_for_level(gallery, item_level, self._data_image_key, self._regex)

            item_images_filtered = remove_duplicate_images(item_images_filtered)

            # check filtered items list isn't empty
            if not(item_images_filtered):
                print(f"❌ No {self._data_image_key} found!")

            item_num = 1

            for figure in item_images_filtered:

                # create path for checking whether image exists
                path_join = os.path.join(self._BASE_DIR,f"{self._data_image_key}_{item_level}{self._regex}", f"{self._data_image_key}_{item_level}_{item_num}{self._regex}.png")

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
        web_scraper = WebScraper(row)

        print(f"🔎 Fetching and downloading {web_scraper._data_image_key}{web_scraper._regex} images...")
        web_scraper._fetch_item_images_and_data()

    print(f"✅ All defensive building images downloaded successfully!")
    