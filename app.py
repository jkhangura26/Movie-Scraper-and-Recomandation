from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import subprocess
import os

app = Flask(__name__)

# Path to movies.csv
MOVIES_CSV = "movies.csv"

# Load movies data
def load_movies():
    if os.path.exists(MOVIES_CSV):
        return pd.read_csv(MOVIES_CSV)
    return pd.DataFrame(columns=["Title", "Year", "Rating", "Genre", "Director", "Cast", "Plot", "Runtime", "Poster"])

# Save movies data
def save_movies(df):
    df.to_csv(MOVIES_CSV, index=False)

# Homepage: Display all movies in a grid
@app.route("/")
def index():
    movies_df = load_movies()
    return render_template("index.html", movies=movies_df.to_dict("records"))

# Movie details and recommendations
@app.route("/movie/<title>")
def movie_details(title):
    movies_df = load_movies()
    movie = movies_df[movies_df["Title"] == title].iloc[0].to_dict()

    # Get recommendations
    recommendations = get_recommendations(title)
    return render_template("movie_details.html", movie=movie, recommendations=recommendations)

# Search functionality
@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    movies_df = load_movies()

    # Check if the movie is already in the database
    if query not in movies_df["Title"].values:
        # Run scraper to add the movie
        result = subprocess.run(
            ["python3", "scraper.py", query],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Reload movies after scraping
            movies_df = load_movies()

    # Redirect to the movie details page if found
    if query in movies_df["Title"].values:
        return redirect(url_for("movie_details", title=query))
    else:
        return "Movie not found and could not be added.", 404

# Get recommendations for a movie
def get_recommendations(title):
    movies_df = load_movies()
    if title not in movies_df["Title"].values:
        return []

    # Run recommend.py to get recommendations
    result = subprocess.run(
        ["python3", "recommend.py", title],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        recommendations = result.stdout.strip().split("\n")
        return recommendations
    return []

if __name__ == "__main__":
    app.run(debug=True)
