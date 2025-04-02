import pandas as pd
import numpy as np

from web_scraper import scrape_item_images

archer_tower_data = {
    "data-image-key": "Archer_Tower",
    "levels": 21,
    "URL": "https://clashofclans.fandom.com/wiki/Archer_Tower/Home_Village"
}

town_hall_data = {
    "data-image-key": "Town_Hall",
    "levels": 17,
    "URL": "https://clashofclans.fandom.com/wiki/Town_Hall"
}

Archer_Tower = pd.DataFrame(archer_tower_data, index=[0])
Town_Hall = pd.DataFrame(town_hall_data, index=[0])

# Main execution
def main():
    scrape_item_images(Town_Hall)
        
main()