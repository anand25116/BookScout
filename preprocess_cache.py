#!/usr/bin/env python3
"""
preprocess_cache.py

Enhances raw book data from the cache using Wikipedia and zero-shot NLP.
Outputs cleaned descriptions and normalized genres.
"""

import pandas as pd
import re
import requests
import time
from bs4 import BeautifulSoup
from transformers import pipeline

# ─── Config ──────────────────────────────────────────────────────────
CACHE_FILE = "cache/book_data.csv"
PLOT_IDS = ["Plot", "Plot_summary", "Summary", "Overview", "Synopsis"]
HEADERS = {"User-Agent": "BookScout/1.0 (contact: devsalot@gmail.com)"}
DELAY_SEC = 1.0

# ─── Zero-Shot Classifier Setup ─────────────────────────────────────
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

CANDIDATE_GENRES = [
    "Fantasy", "Science Fiction", "Horror", "Dystopian", "Adventure",
    "Classic", "Young Adult", "Historical Fiction", "Romance", "Coming-of-age",
    "Satire", "Thriller", "Mystery", "Philosophical Fiction", "Drama", "Self-help",
    "Non-fiction", "Memoir", "Fiction", "Non-Fiction", "Biography",
    "Literary Fiction", "Young-Adult Novel"
]

# ─── Core Utilities ─────────────────────────────────────────────────

def clean_description(desc):
    """Strip HTML tags and whitespace from description."""
    return BeautifulSoup(desc or "", "html.parser").get_text().strip()

def clean_title_for_wiki(title):
    return re.sub(r"\[.*?\]", "", title).strip()

def remove_footnotes(text):
    return re.sub(r"\[\d+\]", "", text)

def classify_genre_with_nli(description, top_n=2):
    """Infer genres from a description using zero-shot classification."""
    if not description or len(description) < 30:
        return ""
    result = classifier(description, CANDIDATE_GENRES, multi_label=True)
    genres = [label for label, score in zip(result["labels"], result["scores"]) if score > 0.4]
    return ", ".join(genres[:top_n]) if genres else ""

def get_wikipedia_plot(title):
    """Fetch plot text from Wikipedia search results."""
    try:
        clean_title = title.split("[")[0].strip()
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "format": "json", "list": "search", "srsearch": clean_title},
            headers=HEADERS, timeout=5
        ).json()
        results = resp.get("query", {}).get("search", [])
        if not results:
            return None, None

        def score(result):
            t = result["title"].lower()
            s = 0
            if "(novel)" in t: s += 100
            if clean_title.lower() in t: s += 50
            if any(bad in t for bad in ["tv", "film", "series"]): s -= 100
            return s

        best = sorted(results, key=score, reverse=True)[0]
        page_title = best["title"]

        html = requests.get(f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}", headers=HEADERS).text
        soup = BeautifulSoup(html, "html.parser")

        for pid in PLOT_IDS:
            header = soup.find(id=pid)
            if header: break
        if not header:
            return None, page_title

        paras = []
        for tag in header.find_all_next():
            if tag.name == "h2": break
            if tag.name == "p": paras.append(tag.get_text(strip=True))

        plot = "\n".join(paras).strip()
        return (plot if len(plot) > 200 else None), page_title

    except Exception:
        return None, None

def extract_wikipedia_categories(page_title):
    """Extract genre/category info from Wikipedia infobox."""
    try:
        html = requests.get(
            f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
            headers=HEADERS, timeout=5
        ).text
        soup = BeautifulSoup(html, "html.parser")
        infobox = soup.find("table", class_=re.compile(r"infobox"))
        if infobox:
            for row in infobox.find_all("tr"):
                th = row.find("th")
                if th and "genre" in th.get_text(strip=True).lower():
                    td = row.find("td")
                    if td:
                        for sup in td.find_all("sup"): sup.decompose()
                        raw = td.get_text(separator=", ")
                        return remove_footnotes(raw).strip()
        return ""
    except Exception as e:
        print(f"📚 Error extracting categories for '{page_title}': {e}")
        return ""

def normalize_categories(cat_str):
    """Standardize categories against the CANDIDATE_GENRES list."""
    parts = [c.strip() for c in cat_str.split(",")]
    mapped = []
    for p in parts:
        for cand in CANDIDATE_GENRES:
            if cand.lower() in p.lower():
                mapped.append(cand)
                break
    seen, out = set(), []
    for m in mapped:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return ", ".join(out)

# ─── Row Processing ────────────────────────────────────────────────

def _process_row(row):
    raw = row.get("description", "")
    clean = clean_description(raw)
    use_wiki = not clean or len(clean) < 30

    cleaned_title = clean_title_for_wiki(row["title"])
    print(f"📚 Enriching: {row['title']} → {cleaned_title}")
    plot, page_title = get_wikipedia_plot(cleaned_title)

    if plot and use_wiki:
        clean = clean_description(plot)
    row["clean_description"] = clean

    wiki_genres = extract_wikipedia_categories(page_title) if page_title else ""
    raw_cats = wiki_genres or classify_genre_with_nli(clean)
    row["categories"] = normalize_categories(raw_cats)

    return row

# ─── Entry Points ─────────────────────────────────────────────────

def preprocess_all():
    df = pd.read_csv(CACHE_FILE)
    if "clean_description" not in df.columns: df["clean_description"] = ""
    if "categories" not in df.columns: df["categories"] = ""

    for idx, row in df.iterrows():
        print(f"🔄 Row {idx+1}/{len(df)}")
        df.iloc[idx] = _process_row(row.copy())
        time.sleep(DELAY_SEC)

    df.to_csv(CACHE_FILE, index=False)
    print("✅ All rows processed and saved.")

def preprocess_last_row():
    df = pd.read_csv(CACHE_FILE)
    if "clean_description" not in df.columns: df["clean_description"] = ""
    if "categories" not in df.columns: df["categories"] = ""

    last_idx = df.index[-1]
    print(f"🔄 Preprocessing last row: {df.loc[last_idx, 'title']}")
    df.iloc[last_idx] = _process_row(df.loc[last_idx].copy())
    df.to_csv(CACHE_FILE, index=False)
    print(f"✅ Finished: {df.loc[last_idx, 'title']}")

if __name__ == "__main__":
    preprocess_all()
