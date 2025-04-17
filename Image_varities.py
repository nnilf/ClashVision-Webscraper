from bs4 import BeautifulSoup
import re

def find_image_varities(soup: BeautifulSoup):
    # Regex to pull out building name and extras
    pattern = re.compile("^[A-Za-z_]+[0-9]+(.*?)(?:-[1-5])?\.png$", re.IGNORECASE)

    # Prepare output
    results = []

    # Find all relevant images
    images = soup.find_all("img", {"data-image-key": True})

    # Define exclusion keywords
    blacklist_keywords = ["pre", "info", "archive", "old", "retired", "test"]
    max_length = 10  # arbitrary limit to skip overly long tags

    # Filtering function
    def is_clean_tag(tag):
        tag_lower = tag.lower()
        if len(tag) > max_length:
            return False
        if any(kw in tag_lower for kw in blacklist_keywords):
            return False
        return True

    # Inside your loop
    for img in images:
        key = img["data-image-key"]
        match = re.match(pattern, key)
        if match:
            extra = match.group(1)
            if (extra == "" or is_clean_tag(extra)) and extra not in results:
                results.append(extra)

    return results
