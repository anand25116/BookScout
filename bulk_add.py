"""
bulk_add.py

Adds books in bulk to the local cache using metadata from Google Books,
with enrichment from Wikipedia and genre classification.

"""

import sys
import time
from app import fetch_book_from_api, save_to_cache
from preprocess_cache import preprocess_last_row

DEFAULT_INPUT_FILE = "scraped_titles.txt"

def load_titles_from_txt(path=None):
    """Load book titles from a text file, one per line."""
    path = path or DEFAULT_INPUT_FILE
    try:
        with open(path, "r", encoding="utf-8") as f:
            titles = [line.strip() for line in f if line.strip()]
        if not titles:
            print(f"File '{path}' is empty.")
        return titles
    except FileNotFoundError:
        print(f"File not found: {path}")
        return []


def fetch_and_cache(title):
    """Fetch book data via API and save it if found."""
    book = fetch_book_from_api(title)
    if book:
        save_to_cache(book)
    return book


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    titles = load_titles_from_txt(path)

    if not titles:
        print("No titles to process. Exiting.")
        return

    print(f"\nStarting bulk add of {len(titles)} titles...\n")

    for idx, title in enumerate(titles, 1):
        print(f"{idx:02d}. 🔍 Processing: {title}")
        book = fetch_and_cache(title)

        if book:
            print(f"Cached: {book['title']}")
            preprocess_last_row()
        else:
            print(f"Failed: {title}")

        time.sleep(1.0)

    print("\nBulk add complete!\n")


if __name__ == "__main__":
    main()
