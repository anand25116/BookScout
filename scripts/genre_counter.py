#!/usr/bin/env python3
"""
genre_counter.py

Counts and normalizes genres from book_data.csv.
Outputs:
    - normalized_genre_counts.csv: CSV of genre frequency
    - genre_options.html: HTML <option> list with genre and counts
"""

import csv
from collections import Counter
import html

CSV_PATH = "cache/book_data.csv"
OUTPUT_CSV = "analysis/normalized_genre_counts.csv"
OUTPUT_OPTIONS = "analysis/genre_options.html"

def normalize(genre):
    """Standardize genre capitalization and spacing."""
    return genre.strip().lower().title()

def count_genres(csv_path):
    """Return a Counter of normalized genre names."""
    counter = Counter()
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cats = row.get("categories", "")
            for cat in cats.split(","):
                n = normalize(cat)
                if n:
                    counter[n] += 1
    return counter

if __name__ == "__main__":
    counts = count_genres(CSV_PATH)

    import os
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Genre", "Count"])
        for genre, cnt in counts.most_common():
            writer.writerow([genre, cnt])

    with open(OUTPUT_OPTIONS, "w", encoding="utf-8") as f:
        for genre, cnt in counts.most_common():
            escaped = html.escape(genre)
            f.write(f'<option value="{escaped}">{escaped} ({cnt})</option>\n')

    print(f"Wrote normalized counts to {OUTPUT_CSV}")
    print(f"Wrote HTML options to {OUTPUT_OPTIONS}")
