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

def get_correct_title_from_csv(input_title, df):
    """Resolve the correct movie title from the CSV."""
    matched_title = None
    highest_similarity = 0.0

    # Iterate over titles in the CSV
    for title in df["Title"]:
        # Compute the similarity score
        similarity_score = get_title_similarity(input_title, title)
        
        if similarity_score > highest_similarity:
            highest_similarity = similarity_score
            matched_title = title

    return matched_title

def get_title_similarity(title1, title2):
    """Compute a simple similarity score between two titles."""
    title1, title2 = title1.lower(), title2.lower()
    
    # Check for simple typo tolerance by calculating the proportion of matching characters
    common_characters = sum(1 for c1, c2 in zip(title1, title2) if c1 == c2)
    return common_characters / max(len(title1), len(title2))

# Assuming the movie name is passed as a command line argument
if len(sys.argv) < 2:
    print("Usage: python reccomend.py \"Movie Name\"")
    sys.exit(1)

# Step 1: Scrape the movie information (calling scraper.py)
movie_name = sys.argv[1]

# Run the scraper.py script for the given movie
subprocess.run(["python3", "scraper.py", movie_name])

# Step 2: Load the CSV file to get the latest movie data
file_path = "movies.csv"  # Update path if needed
movies_df = load_data(file_path)

# Step 3: Resolve the correct title from the CSV (even if there's a typo in the input)
correct_movie_title = get_correct_title_from_csv(movie_name, movies_df)

if correct_movie_title:
    print(f"Using movie title: '{correct_movie_title}' for recommendations.")
else:
    print(f"Movie '{movie_name}' not found in the dataset.")
    sys.exit(1)

# Step 4: Preprocess the data and build the similarity matrix
movies_df = preprocess_data(movies_df)
similarity_matrix = build_similarity_matrix(movies_df)

# Step 5: Get recommendations
recommendations = get_recommendations(correct_movie_title, movies_df, similarity_matrix, top_n=5)

# Display recommendations
print(f"Movies similar to '{correct_movie_title}':")
print(recommendations)
