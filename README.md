#  Clash of Clans AI Base Identifier

An AI-powered base detection system for *Clash of Clans*, using YOLO-based computer vision to identify buildings and recognize base layouts. Also includes a powerful web scraper to gather training data from the Clash of Clans Wiki.

##  What It Does

This project contains two major components:

### 1. YOLO-Based Base Layout Identifier
- Uses a trained YOLOv5/YOLOv8 model to detect buildings on screenshots of Clash of Clans bases.
- Outputs detected structures with bounding boxes and labels.
- Designed to support future automation (attack planning, resource targeting, etc).

### 2. Wiki Image Web Scraper
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
- Optionally scrapes accompanying stats tables.

### AI Detection Pipeline
- Powered by YOLOv5/YOLOv8.
- Trained on a custom dataset of labelled base screenshots.
- Outputs:
  - Detected buildings
  - Class probabilities
  - Exported labels (YOLO format)

---