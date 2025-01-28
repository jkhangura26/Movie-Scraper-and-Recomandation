
# Movie Scraper & Recommendation System

## Overview
This project includes two Python scripts: `scraper.py` and `recommend.py`. 

- `scraper.py` scrapes movie details (such as rating, genre, director, plot, etc.) from IMDb and stores them in a CSV file (`movies.csv`).
- `recommend.py` recommends movies similar to a given movie based on content features using cosine similarity.

## Requirements
- Python 3.x
- Selenium
- BeautifulSoup
- Pandas
- Scikit-learn
- Chrome WebDriver (for Selenium)

## Files

### 1. `scraper.py`
This script is responsible for scraping movie details from IMDb and saving them in a CSV file.

The CSV file `movies.csv` will be updated with new movie data. If `movies.csv` already exists, new entries are appended while avoiding duplicates based on movie title and year.

### 2. `recommend.py`
This script provides movie recommendations based on a given movie's title using a content-based filtering approach. It uses a TF-IDF vectorizer and cosine similarity to compare movie features.

