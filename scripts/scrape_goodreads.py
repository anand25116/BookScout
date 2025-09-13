#!/usr/bin/env python3
"""
scrape_goodreads.py

Scrapes book titles from a Goodreads list and saves only those not already in the cache.
Cleans titles by removing series info like (Book #1) before comparing or saving.
"""

import requests
import csv
import re
from bs4 import BeautifulSoup
import os

CACHE_FILE = "cache/book_data.csv"
DEFAULT_OUTPUT = "data/scraped_titles.txt"

def clean_title(title):
    """Remove bracketed series info like (Book #1)."""
    return re.sub(r"\s*\([^)]*\)", "", title).strip()

def get_cached_titles():
    """Return a set of cleaned, lowercased titles from book_data.csv."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return {clean_title(row["title"]).lower() for row in csv.DictReader(f)}
    except FileNotFoundError:
        return set()

def scrape_titles_to_txt(url, output_path=DEFAULT_OUTPUT):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BookScoutBot/1.0; +https://yourdomain.com)"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page. Status: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    cached_titles = get_cached_titles()
    rows = soup.select("tr[itemtype='http://schema.org/Book']")

    new_titles = []
    for row in rows:
        tag = row.select_one("a.bookTitle")
        if not tag:
            continue
        raw_title = tag.get_text(strip=True)
        cleaned = clean_title(raw_title)
        if cleaned.lower() not in cached_titles:
            new_titles.append(cleaned)

    if new_titles:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for t in new_titles:
                f.write(t + "\n")
        print(f"Saved {len(new_titles)} new titles to {output_path}")
    else:
        print("No new titles found — all already cached.")

if __name__ == "__main__":
    scrape_titles_to_txt("https://www.goodreads.com/list/show/1.Best_Books_Ever")
