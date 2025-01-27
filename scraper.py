import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests

driver = webdriver.Chrome()

# URL of IMDb Top 250
url = "https://www.imdb.com/chart/top"

# Open the IMDb Top 250 page
driver.get(url)
print("Page loaded successfully.")

# Scroll to load all movies (handle lazy loading)
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Parse the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")
movies = soup.select("li.ipc-metadata-list-summary-item")
print(f"Movies found: {len(movies)}")

# Close the Selenium WebDriver
driver.quit()

# Headers for requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# List to store movie data
movie_data = []

# Loop through each movie
for movie in movies:
    try:
        title = movie.select_one("h3.ipc-title__text").text.split(". ")[1]
        year = movie.select_one("span.cli-title-metadata-item").text
        rating = movie.select_one("span.ipc-rating-star--imdb").text.split()[0]
        movie_url = "https://www.imdb.com" + movie.select_one("a.ipc-title-link-wrapper")["href"]

        time.sleep(1)  # Avoid rate limiting

        # Fetch movie page
        movie_page = requests.get(movie_url, headers=headers)
        movie_soup = BeautifulSoup(movie_page.text, "html.parser")

        # Extract details
        genre = ", ".join([g.text for g in movie_soup.select("a[href*='tt_ov_in']")]) or "Not Available"
        director = movie_soup.select_one("a[href*='tt_ov_dr']").text if movie_soup.select_one("a[href*='tt_ov_dr']") else "Not Available"
        cast = ", ".join([c.text.strip() for c in movie_soup.select("a[href*='tt_ov_st']")[1:4]]) if movie_soup.select("a[href*='tt_ov_st']") else "Not Available"
        plot = movie_soup.select_one("span[data-testid='plot-xl']").text if movie_soup.select_one("span[data-testid='plot-xl']") else "Not Available"
        runtime = movie_soup.select_one("li[data-testid='title-techspec_runtime']").text.replace("Runtime", "").strip() if movie_soup.select_one("li[data-testid='title-techspec_runtime']") else "Not Available"
        poster = movie_soup.select_one("img.ipc-image")["src"] if movie_soup.select_one("img.ipc-image") else "Not Available"

        movie_data.append({
            "Title": title,
            "Year": year,
            "Rating": rating,
            "Genre": genre,
            "Director": director,
            "Cast": cast,
            "Plot": plot,
            "Runtime": runtime,
            "Poster": poster
        })

        print(f"Scraped: {title}")

    except Exception as e:
        print(f"Error scraping movie: {e}")

# Save to CSV
pd.DataFrame(movie_data).to_csv("imdb_top_250_movies.csv", index=False)
print("Scraping complete! Data saved.")