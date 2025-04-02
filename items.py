import pandas as pd

from web_scraper import scrape_item_images

# reading csv file 
defenisve_df = pd.read_csv("csv/defensive_buildings.csv")
defenisve_df = defenisve_df.fillna("")

town_hall_data = [["Town_Hall",17,"https://clashofclans.fandom.com/wiki/Town_Hall"]]
town_hall_df = pd.DataFrame(town_hall_data, columns=["data-image-key", "levels", "URL"])

# Main execution
def execute_web_scraper():
    scrape_item_images(defenisve_df)
        
execute_web_scraper()