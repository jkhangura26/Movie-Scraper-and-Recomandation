from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import subprocess
import os

app = Flask(__name__)
MOVIES_CSV = "movies.csv"

def load_movies():
    if os.path.exists(MOVIES_CSV):
        return pd.read_csv(MOVIES_CSV)
    return pd.DataFrame(columns=["Title", "Year", "Rating", "Genre", "Director", "Cast", "Plot", "Runtime", "Poster"])

def save_movies(df):
    df.to_csv(MOVIES_CSV, index=False)

@app.route("/")
def index():
    movies_df = load_movies()
    return render_template("index.html", movies=movies_df.to_dict("records"))

@app.route("/movie/<title>")
def movie_details(title):
    movies_df = load_movies()
    try:
        movie = movies_df[movies_df["Title"] == title].iloc[0].to_dict()
    except:
        return "Movie not found", 404
    
    # Get recommendations
    result = subprocess.run(
        ["python", "recommend.py", title],
        capture_output=True,
        text=True
    )
    
    recommendations = []
    if result.returncode == 0:
        recommendations = result.stdout.strip().split("\n")
        recommendations = [r for r in recommendations if r]  # Filter empty strings

    return render_template("movie_details.html", 
                         movie=movie, 
                         recommendations=recommendations)

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query").strip()
    if not query:
        return redirect(url_for("index"))
    
    movies_df = load_movies()
    
    # Attempt to find an exact match (ignoring case)
    matched_title = None
    for title in movies_df["Title"]:
        if query.lower() == title.lower():
            matched_title = title
            break

    # If no exact match is found, run the scraper.
    if not matched_title:
        result = subprocess.run(
            ["python", "scraper.py", query],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Error adding movie: {result.stderr}", 500
        
        # Get the proper title from the scraper's output (first non-empty line)
        scraper_output = result.stdout.strip()
        if scraper_output:
            proper_title = next((line.strip() for line in scraper_output.splitlines() if line.strip()), None)
        else:
            proper_title = None

        # Reload the CSV to pick up any newly added movie.
        movies_df = load_movies()
        if proper_title:
            for title in movies_df["Title"]:
                if proper_title.lower() == title.lower():
                    matched_title = title
                    break
            # If no match is found in the CSV, default to the scraped title.
            if not matched_title:
                matched_title = proper_title

    if matched_title:
        return redirect(url_for("movie_details", title=matched_title))
    else:
        return "Movie not found and could not be added.", 404

if __name__ == "__main__":
    app.run(debug=True)