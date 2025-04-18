import pandas as pd
from web_scraper import download_item_images_and_data

def scrape_item_images(item_df: pd.DataFrame):
    """
    Executes the higher level function of web scraping and downloads

    :param item_df: df of all the items in which web scraping needs to be applied on,
    containing: URL, data-image-key and levels
    :returns: Directory saved with all images of items from item_df
    """

    for index, row in item_df.iterrows():

        data_image_key = row["data-image-key"]

        print(f"🔎 Fetching and downloading {data_image_key} images...")

        download_item_images_and_data(row)

        print(f"✅ Fetched and downloaded {data_image_key} images...")

    print(f"✅ All defensive building images downloaded successfully!")


def main():
    # reading csv file 
    defenisve_df = pd.read_csv("csv/home_village_buildings-2.csv")

    town_hall_data = [["Town_Hall",17,"https://clashofclans.fandom.com/wiki/Town_Hall"]]
    town_hall_df = pd.DataFrame(town_hall_data, columns=["data-image-key", "levels", "URL"])

    scrape_item_images(defenisve_df)

if __name__ == "__main__":
    main()