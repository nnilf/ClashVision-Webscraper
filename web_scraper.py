import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO
import time
from utils import filter_images_for_level, remove_duplicate_images, get_max_level, find_image_varities
from parse_damage_table import get_building_stats


def save_data(soup: BeautifulSoup, BASE_DIR, data_image_key: str):
    """Gets the children of current element which is all the Nodes next to the current node.

        Args:
            soup: BeautifulSoup element containing page html
            BASE_DIR: base directory in which the data is to be saved to
            data_image_key: Title of the current building

        Returns:
            levels: maximum level of the current building
    """
    df_path =  os.path.join(BASE_DIR, f"{data_image_key}_data.csv")

    if os.path.isfile(df_path):
        print(f"✅ Skipped {data_image_key} data, due to it already existing")
        df = pd.read_csv(df_path)
        levels = get_max_level(df)
    else:
        if data_image_key == "Giga_Tesla":
            stats = get_building_stats(soup, True)
        else:
            stats = get_building_stats(soup)
        if not(stats):
            raise ValueError(f"Failed to find data for '{data_image_key}'")
        for key in stats.keys():
            if key == "Main Stats":
                df = stats[key]
                levels = get_max_level(df)
                df.to_csv(df_path, index=False)
                print(f"✅ Saved: {df_path}")
            else:
                key_text = key.replace(" ", "_")
                df_path = os.path.join(BASE_DIR, f"{data_image_key}_{key_text}_data.csv")
                df.to_csv(df_path, index=False)
                print(f"✅ Saved: {df_path}")
        
    return levels


def download_item_images_and_data(item_df: pd.DataFrame):
    """Retrieves and downloads images for every level of a the building supplied by the df

        Args:
            item_df: dataframe containing information for one building

        Returns:
            downloads image of the building for all of its variations and levels
    """
    # intialise df variables
    data_image_key = item_df["data-image-key"]
    WIKI_URL = item_df["URL"]

    # create directory string for directory path to be created
    BASE_DIR = "items\\" + data_image_key

    # create directory path
    os.makedirs(BASE_DIR, exist_ok=True)

    # Headers to mimic a real browser request
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(WIKI_URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    levels = save_data(soup, BASE_DIR, data_image_key)

    if data_image_key == "X-Bow":
        pass
    image_varities = find_image_varities(soup)

    for variety in image_varities:

        # set variety to current variety
        regex = variety

        # find all images for that particular variety
        gallery = soup.find_all("img", attrs={"data-image-key": re.compile(f"{data_image_key}\d+(-[1-5])?{regex}\.png")})

        if not(gallery):
            print(f"❌ Failed to find Images for '{data_image_key}{regex}'")
            continue

        for item in range(levels):
            item_level = item + 1

            # Find all images for item
            item_images_filtered = filter_images_for_level(gallery, item_level, data_image_key, regex)

            item_images_filtered = remove_duplicate_images(item_images_filtered)

            item_num = 1

            for figure in item_images_filtered:

                # create path for checking whether image exists
                path_join = os.path.join(BASE_DIR,f"{data_image_key}_{regex}", f"{data_image_key}_{item_level}_{item_num}{regex}.png")

                # check whether image already exists
                if os.path.isfile(path_join):
                    print(f"✅ Skipped {data_image_key}_{item_level}_{item_num}{regex} due to the image already existing")
                    # increment item number and then skip over item
                    item_num += 1
                    continue

                if figure and "data-src" in figure.attrs:
                    img_url = figure["data-src"]
                    
                    img_url = img_url.split("/revision")[0]  # Remove unnecessary URL parts

                    download_image_and_data(img_url, item_level, item_num, BASE_DIR, data_image_key, regex)

                item_num += 1


def download_image_and_data(img_url, level, item_num, BASE_DIR, data_image_key, regex):
    """Downloads image from provided URL.

        Args:
            img_url: single URL of an image
            level: the level of the given image
            item_num: current building variation if there is any
            BASE_DIR: base directory for the images to be saved too
            data_image_key: current building title
            regex: regex for building variations if there is any

        Returns:
            Image saved to base directory
    """
    folder_path = os.path.join(BASE_DIR,f"{data_image_key}_{regex}")
    os.makedirs(folder_path, exist_ok=True)

    try:
        response = requests.get(img_url, stream=True)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        image_format = image.format.lower() 
        image_path = os.path.join(folder_path, f"{data_image_key}_{level}_{item_num}{regex}.{image_format}")

        image.save(image_path)
        print(f"✅ Saved: {image_path}")

        time.sleep(1)  # Avoid hitting the server too fast
    except Exception as e:
        print(f"❌ Failed to download {data_image_key}_{level}_{item_num} image: {e}")