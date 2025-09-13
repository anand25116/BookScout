"""
clean_categories.py

Removes invalid or non-informative entries from the 'categories' column
of the book data cache (e.g., stray parentheses, blank commas).
"""

import pandas as pd
import re
import os

CACHE_FILE = "cache/book_data.csv"

def clean_category_list(cat_str):
    """
    Given a comma-separated category string, drop any entry that
    contains no alphanumeric characters (e.g., '(', ')', or empty).
    """
    parts = [c.strip() for c in cat_str.split(',')]
    cleaned = [c for c in parts if re.search(r'\w', c)]
    return ", ".join(cleaned)

def main():
    if not os.path.exists(CACHE_FILE):
        print(f"File not found: {CACHE_FILE}")
        return

    df = pd.read_csv(CACHE_FILE)

    if 'categories' not in df.columns:
        print("No 'categories' column found in the cache.")
        return

    before_counts = df['categories'].str.count(',').sum()
    df['categories'] = df['categories'].fillna('').apply(clean_category_list)
    after_counts = df['categories'].str.count(',').sum()

    df.to_csv(CACHE_FILE, index=False)
    print(f"Cleaned categories in {len(df)} rows.")
    print(f"Total category items before: {before_counts}, after: {after_counts}")
    print(f"Saved cleaned data to: {CACHE_FILE}")

if __name__ == "__main__":
    main()
