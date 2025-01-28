import pandas as pd
import sys
import subprocess
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_data(file_path):
    """Load movies dataset from CSV file."""
    return pd.read_csv(file_path)

def preprocess_data(df):
    """Combine important features into a single text field for vectorization."""
    df = df.fillna("")  # Fill missing values with empty strings
    df["combined_features"] = df.apply(lambda row: 
        f"{row['Title']} {row['Year']} {row['Rating']} {row['Genre']} {row['Director']} {row['Cast']} {row['Plot']} {row['Runtime']}", axis=1)
    return df

def build_similarity_matrix(df):
    """Create a TF-IDF vectorized similarity matrix."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df["combined_features"])
    return cosine_similarity(tfidf_matrix, tfidf_matrix)

def get_recommendations(movie_title, df, similarity_matrix, top_n=5):
    """Find similar movies based on the given title."""
    if movie_title not in df["Title"].values:
        return f"Movie '{movie_title}' not found in dataset."

    # Get index of the input movie
    idx = df[df["Title"] == movie_title].index[0]

    # Get similarity scores
    similarity_scores = list(enumerate(similarity_matrix[idx]))

    # Sort by similarity score in descending order
    sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Get top N similar movies (excluding the input movie itself)
    top_movies = [df.iloc[i[0]]["Title"] for i in sorted_scores[1:top_n+1]]
    
    return top_movies

# Check for command line argument
if len(sys.argv) < 2:
    print("Usage: python3 reccomend.py \"Movie Name\"")
    sys.exit(1)

movie_name = sys.argv[1]  # Get the movie name from the command line argument

# Call the scraper.py script to scrape the movie details
print(f"Scraping movie details for: {movie_name}")
subprocess.run(['python3', 'scraper.py', movie_name])

# Load and process the data
file_path = "movies.csv"  # Update path if needed
movies_df = load_data(file_path)
movies_df = preprocess_data(movies_df)
similarity_matrix = build_similarity_matrix(movies_df)

# Get recommendations
recommendations = get_recommendations(movie_name, movies_df, similarity_matrix, top_n=5)

print(f"Movies similar to '{movie_name}':")
print(recommendations)
