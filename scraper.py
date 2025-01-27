import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL of IMDb Top 250
url = "https://www.imdb.com/chart/top"

# Headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Send a GET request
response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)  # Debug: Check if the request is successful
soup = BeautifulSoup(response.text, "html.parser")

# Select movie rows
movies = soup.select("li.ipc-metadata-list-summary-item")
print(f"Movies found: {len(movies)}")  # Debugging: Check how many movies are being detected

# List to store movie data
movie_data = []

# Loop through each movie
for movie in movies:
    try:
        title = movie.select_one("h3.ipc-title__text").text.split(". ")[1]
        year = movie.select_one("span.cli-title-metadata-item").text
        rating = movie.select_one("span.ipc-rating-star--imdb").text.split()[0]
        movie_url = "https://www.imdb.com" + movie.select_one("a.ipc-title-link-wrapper")["href"]

        # Sleep to avoid rate limiting
        time.sleep(1)

        # Fetch movie page
        movie_page = requests.get(movie_url, headers=headers)
        movie_soup = BeautifulSoup(movie_page.text, "html.parser")

        # Extract genre correctly
        genre_elements = movie_soup.select("div[data-testid='genres'] a")
        genre = ", ".join([g.text for g in genre_elements]) if genre_elements else "Not Available"

        # Extract director
        director_element = movie_soup.select_one("a[href*='tt_ov_dr']")
        director = director_element.text if director_element else "Not Available"

        # Extract cast (first 3 actors)
        cast_elements = movie_soup.select("a[href*='tt_ov_st']")
        cast = ", ".join([c.text.strip() for c in cast_elements[:3]]) if cast_elements else "Not Available"

        # Extract plot
        plot_element = movie_soup.select_one("span[data-testid='plot-xl']")
        plot = plot_element.text if plot_element else "Not Available"

        # Extract runtime correctly without extra text
        runtime_element = movie_soup.select_one("li[data-testid='title-techspec_runtime']")
        runtime = runtime_element.text.replace("Runtime", "").strip() if runtime_element else "Not Available"

        # Extract poster
        poster_element = movie_soup.select_one("img.ipc-image")
        poster = poster_element["src"] if poster_element else "Not Available"

        # Append to list
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
        print(f"Error scraping {title}: {e}")

# Convert to DataFrame and save
df = pd.DataFrame(movie_data)
df.to_csv("imdb_top_250_movies.csv", index=False)

print("Scraping complete! Data saved.")
