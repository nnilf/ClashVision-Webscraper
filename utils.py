import re
from bs4 import Tag

def filter_images(img_elements, level, data_image_key, regex):
    """
    Filters <img> elements to only include those images from that particular building level.

    :param img_elements: List of image elements.
    :param level: Level that is wanted to be retrieved.
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