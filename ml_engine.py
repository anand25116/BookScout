"""
ml_engine.py

Generates content-based book recommendations using TF-IDF on descriptions + genres,
with optional genre filtering. Combines unstructured and structured features.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.sparse import hstack

CACHE_FILE = 'cache/book_data.csv'


def load_and_vectorize(csv_path=CACHE_FILE):
    """Loads book data and returns TF-IDF + genre matrix."""
    df = pd.read_csv(csv_path)

    df = df[df['clean_description'].notnull() & (df['clean_description'].str.strip() != "")]
    df.reset_index(drop=True, inplace=True)

    df['categories'] = df['categories'].fillna('')
    df['combined_text'] = df['clean_description'] + ' ' + df['categories'].str.lower()

    tfidf = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8
    )
    tfidf_matrix = tfidf.fit_transform(df['combined_text'])

    cat_split = df['categories'].str.lower().str.split(', ')
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(cat_split)

    combined_matrix = hstack([tfidf_matrix, genre_matrix * 0.5]).tocsr()

    return df, combined_matrix


def get_similar_books(title, filter_genres=None, top_n=5, csv_path=CACHE_FILE):
    """
    Returns top_n books most similar to `title`.

    Params:
    - title: str — the seed book title to compare others against
    - filter_genres: list[str] — optional genre filters
    - top_n: int — number of results to return
    """
    df, combined_matrix = load_and_vectorize(csv_path)

    matches = df.index[df['title'].str.lower() == title.lower()]
    if matches.empty:
        print(f"Title '{title}' not found in cache.")
        return []

    idx = matches[0]
    sims = cosine_similarity(combined_matrix[idx], combined_matrix).flatten()

    sorted_indices = sims.argsort()[::-1]

    results = []
    for i in sorted_indices:
        if i == idx:
            continue

        if filter_genres:
            book_cats = [g.strip().lower() for g in df.at[i, 'categories'].split(',')]
            if not any(fg.lower() in book_cats for fg in filter_genres):
                continue

        results.append({
            'title': df.at[i, 'title'],
            'author': df.at[i, 'author'],
            'categories': df.at[i, 'categories'],
            'rating': df.at[i, 'rating'],
            'clean_description': df.at[i, 'clean_description'],
            'similarity': round(float(sims[i]), 2)
        })

        if len(results) >= top_n:
            break

    return results
