import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the IMDb Top 250 page
url = "https://www.imdb.com/chart/top"

# Headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Send a GET request to the URL
response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)  # Debug: Check if the request is successful

# Parse the HTML content
soup = BeautifulSoup(response.text, "html.parser")

# Find all movie rows in the table
movies = soup.select("li.ipc-metadata-list-summary-item")

# Initialize a list to store movie data
movie_data = []

# Loop through each movie row
for movie in movies:
    # Extract movie details
    title = movie.select_one("h3.ipc-title__text").text.split(". ")[1]  # Extract title without rank
    year = movie.select_one("span.cli-title-metadata-item").text  # Release year
    rating = movie.select_one("span.ipc-rating-star--imdb").text.split()[0]  # Rating
    movie_url = "https://www.imdb.com" + movie.select_one("a.ipc-title-link-wrapper")["href"]  # Movie URL

    # Scrape additional details from the movie's individual page
    movie_page = requests.get(movie_url, headers=headers)
    movie_soup = BeautifulSoup(movie_page.text, "html.parser")

    # Extract genre, director, cast, and plot summary
    try:
        genre = ", ".join([g.text for g in movie_soup.select("a.ipc-chip--on-baseAlt")])  # Genres
    except:
        genre = "N/A"

    try:
        director = movie_soup.select("a.ipc-metadata-list-item__list-content-item")[0].text  # Director
    except:
        director = "N/A"

    try:
        cast = ", ".join([c.text for c in movie_soup.select("a.ipc-metadata-list-item__list-content-item")[1:4]])  # Top 3 cast members
    except:
        cast = "N/A"

    try:
        plot = movie_soup.select("span.sc-5f699a2e-0")[0].text.strip()  # Plot summary
    except:
        plot = "N/A"

    try:
        runtime = movie_soup.select("li.ipc-inline-list__item")[-1].text  # Runtime
    except:
        runtime = "N/A"

    try:
        poster = movie_soup.select("img.ipc-image")[0]["src"]  # Poster image URL
    except:
        poster = "N/A"

    # Append the data to the list
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

# Convert the list to a DataFrame
df = pd.DataFrame(movie_data)

# Save the data to a CSV file
df.to_csv("imdb_top_250_movies.csv", index=False)

print("Scraping complete! Data saved to 'imdb_top_250_movies.csv'.")