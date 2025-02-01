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
    
    # Check if a movie exists (using case-insensitive substring matching)
    matched_title = None
    for title in movies_df["Title"]:
        if query.lower() in title.lower():
            matched_title = title
            break

    if not matched_title:
        # Run the scraper to add the movie if not found
        result = subprocess.run(
            ["python", "scraper.py", query],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Error adding movie: {result.stderr}", 500
        
        # The scraper is expected to print the proper title of the movie to stdout.
        scraper_output = result.stdout.strip()
        if scraper_output:
            # Take the first valid line (i.e. the proper movie title) from the scraper output.
            proper_title = next((line.strip() for line in scraper_output.splitlines() if line.strip()), None)
            if proper_title:
                # Reload movies.csv to pick up the new entry
                movies_df = load_movies()
                # Now try to find an exact match for the proper title.
                for title in movies_df["Title"]:
                    if proper_title.lower() == title.lower():
                        matched_title = title
                        break
    
    if matched_title:
        return redirect(url_for("movie_details", title=matched_title))
    else:
        return "Movie not found and could not be added.", 404

if __name__ == "__main__":
    app.run(debug=True)