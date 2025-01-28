import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_data(file_path):
    """Loads movie data from a CSV file."""
    return pd.read_csv(file_path)

def preprocess_data(df):
    """Combines important text fields for vectorization."""
    df['combined_features'] = df['Genre'] + ' ' + df['Director'] + ' ' + df['Cast']
    return df

def build_similarity_matrix(df):
    """Computes the cosine similarity matrix based on combined text features."""
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['combined_features'].fillna(''))
    return cosine_similarity(tfidf_matrix)

def get_recommendations(movie_title, df, similarity_matrix, top_n=5):
    """Returns top N recommended movies based on similarity."""
    if movie_title not in df['Title'].values:
        return f"Movie '{movie_title}' not found in dataset."
    
    idx = df[df['Title'] == movie_title].index[0]
    similar_scores = list(enumerate(similarity_matrix[idx]))
    similar_scores = sorted(similar_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    
    recommended_movies = [df.iloc[i[0]]['Title'] for i in similar_scores]
    return recommended_movies

# Example Usage
if __name__ == "__main__":
    file_path = "movies.csv" 
    df = load_data(file_path)
    df = preprocess_data(df)
    similarity_matrix = build_similarity_matrix(df)
    
    movie_name = "Oppenheimer"
    recommendations = get_recommendations(movie_name, df, similarity_matrix)
    print("Recommended movies for", movie_name, ":", recommendations)
