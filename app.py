from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import csv
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from preprocess_cache import preprocess_last_row
from ml_engine import get_similar_books

# ─── Environment Setup ──────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

# ─── Flask App Setup ────────────────────────────────────────────────
app = Flask(__name__)
CACHE_FILE = "cache/book_data.csv"

# ─── Static Genre List ──────────────────────────────────────────────
CANDIDATE_GENRES = [
    "Fantasy", "Science Fiction", "Horror", "Dystopian", "Adventure", "Classic",
    "Young Adult", "Historical Fiction", "Romance", "Coming-of-age", "Satire",
    "Thriller", "Mystery", "Philosophical Fiction", "Drama", "Self-help",
    "Non-fiction", "Memoir", "Fiction", "Non-Fiction", "Biography",
    "Literary Fiction", "Young-Adult Novel"
]

# ─── Ensure Cache Directory Exists ─────────────────────────────────
os.makedirs("cache", exist_ok=True)

# ─── Core Utilities ────────────────────────────────────────────────
def get_cached_book(title):
    """Return cached book row dict for a given title, or None."""
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["title"].strip().lower() == title.strip().lower():
                return row
    return None

def save_to_cache(book):
    """Append a new book dict to the CSV if not already present."""
    existing = set()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row["title"].lower())

    if book["title"].lower() in existing:
        return

    file_exists = os.path.isfile(CACHE_FILE)
    with open(CACHE_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=book.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(book)

def clean_description(text):
    """Strip HTML tags from text."""
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text().strip()

def fetch_book_from_api(title):
    """
    Fetch metadata from Google Books. Returns a dict matching the CSV schema.
    Wikipedia fallback is handled in preprocess_last_row().
    """
    params = {"q": f"intitle:{title}", "maxResults": 1}
    if API_KEY:
        params["key"] = API_KEY

    response = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
    data = response.json()

    if "items" not in data:
        return None

    info = data["items"][0]["volumeInfo"]
    book = {
        "title": info.get("title", ""),
        "author": ", ".join(info.get("authors", [])),
        "description": info.get("description", ""),
        "clean_description": clean_description(info.get("description", "")),
        "categories": ", ".join(info.get("categories", [])),
        "rating": info.get("averageRating", "N/A")
    }

    save_to_cache(book)
    return book

# ─── Flask Routes ───────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    selected_genres = request.form.getlist("genres") if request.method == "POST" else []
    book_data = None

    if request.method == "POST":
        title = request.form["title"].strip()
        book_data = get_cached_book(title)
        if not book_data:
            book_data = fetch_book_from_api(title)
            if book_data:
                preprocess_last_row()

        if book_data:
            return redirect(
                url_for('recommend', title=book_data['title'], genres=",".join(selected_genres))
            )

    return render_template(
        "index.html",
        candidate_genres=CANDIDATE_GENRES,
        selected_genres=selected_genres
    )

@app.route("/recommend")
def recommend():
    title = request.args.get("title")
    genre_filter = request.args.get("genres", "")
    genre_filter = [g for g in genre_filter.split(",") if g] if genre_filter else []

    if not title:
        return redirect(url_for("index"))

    recommendations = get_similar_books(
        title,
        filter_genres=genre_filter,
        top_n=5
    )

    return render_template(
        "results.html",
        title=title,
        recommendations=recommendations,
        genre_filter=genre_filter
    )

# ─── Entry Point ────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
