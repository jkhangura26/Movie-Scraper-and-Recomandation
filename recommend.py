import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
    try:
        idx = df[df["Title"] == movie_title].index[0]
        similarity_scores = list(enumerate(similarity_matrix[idx]))
        sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        return [df.iloc[i[0]]["Title"] for i in sorted_scores[1:top_n+1]]
    except:
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python recommend.py \"Movie Name\"")
        sys.exit(1)

    movie_title = sys.argv[1]
    df = load_data("movies.csv")
    df = preprocess_data(df)
    similarity_matrix = build_similarity_matrix(df)
    recommendations = get_recommendations(movie_title, df, similarity_matrix)
    
    if recommendations:
        print("\n".join(recommendations))
    else:
        print(f"No recommendations found for {movie_title}")