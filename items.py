import pandas as pd

from web_scraper import scrape_item_images

defensive_building_data = [["Archer_Tower", 21, "https://clashofclans.fandom.com/wiki/Archer_Tower/Home_Village"],
                           ["Town_Hall", 17, "https://clashofclans.fandom.com/wiki/Town_Hall"],
                           ["Cannon", 21, "https://clashofclans.fandom.com/wiki/Cannon"]]

defenisve_df = pd.DataFrame(defensive_building_data, columns = ["data-image-key", "levels", "URL"])

# Main execution
def execute_web_scraper():
    scrape_item_images(defenisve_df)
        
execute_web_scraper()