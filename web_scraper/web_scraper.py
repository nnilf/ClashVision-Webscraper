import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
import re
from bing_image_downloader import downloader

# Base directory for saving images
BASE_DIR = "town_halls"
os.makedirs(BASE_DIR, exist_ok=True)

# URL of the Town Hall wiki page
WIKI_URL = "https://clashofclans.fandom.com/wiki/Town_Hall"

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def filter_town_hall_images(img_elements, town_hall_level):
    """Filters <img> elements to only include those with a matching data-image-key."""
    pattern = re.compile(f"Town_Hall{town_hall_level}(-[1-5])?\.png")  # Matches TownHall7, TownHall7-1 to TownHall7-5
    
    return [
        img for img in img_elements 
        if img.has_attr("data-image-key") and pattern.match(img["data-image-key"])
    ]

# Function to scrape Town Hall images
def fetch_town_hall_images():
    response = requests.get(WIKI_URL, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to fetch the Town Hall Wiki page.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    th_images = [[] for i in range(17)]
    
    for town_hall in range(17):
        town_hall_level = town_hall + 1
        # Find all images for that town hall
        gallery = soup.find_all("img", attrs={"data-image-key": re.compile(f"Town_Hall\d+(-[1-5])?\.png")})
        gallery = filter_town_hall_images(gallery, town_hall_level)

        for figure in gallery:
            if figure and "data-src" in figure.attrs:
                img_url = figure["data-src"]
                
                # Some images have low-resolution links; fetch the higher-quality version
                img_url = img_url.split("/revision")[0]  # Remove unnecessary URL parts
                
                th_images[town_hall].append(img_url)

    return th_images

# Function to download images and save them in folders
def download_images(th_images):
    level = 1
    for th_level in th_images:
        folder_path = os.path.join(BASE_DIR, f"town_hall_{level}")
        os.makedirs(folder_path, exist_ok=True)

        for images in range(len(th_level)):
            try:
                response = requests.get(th_level[images], stream=True)
                response.raise_for_status()

                image = Image.open(BytesIO(response.content))
                image_format = image.format.lower()
                image_path = os.path.join(folder_path, f"th{level}_{images+1}.{image_format}")

                image.save(image_path)
                print(f"✅ Saved: {image_path}")

                time.sleep(1)  # Avoid hitting the server too fast
            except Exception as e:
                print(f"❌ Failed to download TH{level} image: {e}")
        
        level += 1

# Main execution
def main():
    print("🔎 Fetching Town Hall images...")
    town_hall_images = fetch_town_hall_images()
    
    if town_hall_images:
        print("📥 Downloading images...")
        download_images(town_hall_images)
        print("✅ All Town Hall images downloaded successfully!")
    else:
        print("❌ No images found!")
        
if __name__ == "__main__":
    main()