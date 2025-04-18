import re
from bs4 import Tag
import pandas as pd
from bs4 import BeautifulSoup

def filter_images_for_level(img_elements, level, data_image_key, regex):
    """
    Filters <img> elements to only include those images from that particular building level.

    :param img_elements: List of image elements.
    :param level: Level that is wanted to be retrieved.
    :param data_image_key: data image key for the current building
    :param regex: any extra regex required for defining specific building types
    :return: List of image elements that match that particular level.
    """
    pattern = re.compile(f"{data_image_key}{level}(-[1-5])?{regex}\.png")

    return [
        img for img in img_elements 
        if img.has_attr("data-image-key") and pattern.match(img["data-image-key"])
    ]


def remove_duplicate_images(img_elements):
    """
    Removes duplicate image elements based on their 'data-image-key' attribute using regex masks.

    :param img_elements: List of image elements.
    :return: List of unique image elements.
    """
    unique_imgs = list({img['data-image-key'].strip(): img for img in img_elements if isinstance(img, Tag) and img.has_attr('data-image-key')}.values())

    return unique_imgs


def get_max_level(df: pd.DataFrame) -> int:
    """Returns the highest level of a building using stats table dataframe"""
    max_level = df["Level"][len(df)-1]
    return int(max_level)


# Filtering function
def is_clean_tag(tag):

    # Define exclusion keywords
    blacklist_keywords = ["pre", "info", "archive", "old", "retired", "test"]
    max_length = 10  # arbitrary limit to skip overly long tags

    tag_lower = tag.lower()
    if len(tag) > max_length:
        return False
    if any(kw in tag_lower for kw in blacklist_keywords):
        return False
    return True


def clean_text(text: str) -> str:
    """Clean wiki text formatting"""
    return re.sub(r'\[.*?\]|Edit|\.|\u200e|\u202f', '', text).strip()


def clean_cell(text: str):
    """Clean and convert cell values"""
    text = clean_text(text)
    if text.replace(',', '').replace('.', '').isdigit():
        return float(text.replace(',', '')) if '.' in text else int(text.replace(',', ''))
    if text.endswith('%'):
        try:
            return float(text[:-1]) / 100
        except ValueError:
            pass
    if text.lower() in ('n/a', '?', '-', '', 'none'):
        return None
    return text


def find_image_varities(soup: BeautifulSoup):
    # Regex to pull out building name and extras
    pattern = re.compile("^[A-Za-z_]+[0-9]+(.*?)(?:-[1-5])?\.png$", re.IGNORECASE)

    # Prepare output
    results = []

    # Find all relevant images
    images = soup.find_all("img", {"data-image-key": True})

    # Inside your loop
    for img in images:
        key = img["data-image-key"]
        match = re.match(pattern, key)
        if match:
            extra = match.group(1)
            if (extra == "" or is_clean_tag(extra)) and extra not in results:
                results.append(extra)

    return results