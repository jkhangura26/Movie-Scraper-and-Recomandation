import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
import sys

def load_data(file_path):
    """Load movies dataset from CSV file."""
    return pd.read_csv(file_path)

def preprocess_data(df):
    """Combine important features into a single text field for vectorization."""
    df = df.fillna("")
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

if len(sys.argv) < 2:
    print("Usage: python reccomend.py \"Movie Name\"")
    sys.exit(1)

# Step 1: Scrape the movie information (calling scraper.py)
movie_name = sys.argv[1]

# Run the scraper.py script and capture output
result = subprocess.run(
    ["python3", "scraper.py", movie_name],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("Error running scraper:")
    print(result.stderr)
    sys.exit(1)

# Extract processed titles from stdout
scraper_output = result.stdout.strip()
if not scraper_output or scraper_output == "No titles processed.":
    print(f"No valid titles found for '{movie_name}'. Exiting.")
    sys.exit(1)

processed_titles = scraper_output.split('\n')
correct_movie_title = processed_titles[0]  # Use the first title found

# Step 2: Load data and check title existence
file_path = "movies.csv"
movies_df = load_data(file_path)
if correct_movie_title not in movies_df["Title"].values:
    print(f"'{correct_movie_title}' not found in dataset after scraping.")
    sys.exit(1)

# Proceed with recommendations
movies_df = preprocess_data(movies_df)
similarity_matrix = build_similarity_matrix(movies_df)
recommendations = get_recommendations(correct_movie_title, movies_df, similarity_matrix)

print(f"Movies similar to '{correct_movie_title}':")
print(recommendations)