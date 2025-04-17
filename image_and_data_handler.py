from PIL import Image
import os
import requests
from io import BytesIO
import time

def download_image_and_data(img_url, level, item_num, BASE_DIR, data_image_key, regex):
    """
    Downloads images from provided list of URLs.

    :param img_url: single URL of an image.
    :param level: the level of the given image
    :param item_num: the number of the current variation of the item
    :param BASE_DIR: base directory for paths to download images to
    :param data_image_key: data image key for the current building
    :param regex: any extra regex required for defining specific building types
    :param data_df: df containing level, damage per second, damage per shot, hitpoints
    :return: downloads the image to its file directory
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