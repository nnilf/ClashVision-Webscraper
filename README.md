#  Clash of Clans Wiki Image Web Scraper

A powerful web scraper to gather training data from the Clash of Clans Wiki.

##  What It Does

### Wiki Image Web Scraper
- Scrapes building images and level variants directly from the [Clash of Clans Fandom Wiki](https://clashofclans.fandom.com).
- Filters and downloads images level-wise (e.g. Town Hall 1–15).
- Also scrapes stat tables associated with each building (hitpoints, DPS, etc).
- Prepares dataset directories for computer vision training.

---

##  How It Works

###  Web Scraper
- Uses `requests` and `BeautifulSoup` to navigate and parse Wiki pages.
- Filters relevant images using `data-image-key` and level-based regex.
- Downloads images into organized folders.
- Scrapes accompanying stats tables.

---