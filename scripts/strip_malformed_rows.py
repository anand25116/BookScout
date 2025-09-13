"""
strip_malformed_rows.py

Scans the cached book_data.csv and writes a cleaned copy with only
rows that match the expected number of columns.
"""

import csv
import os

INPUT_FILE = "cache/book_data.csv"
OUTPUT_FILE = "cache/book_data_cleaned.csv"
EXPECTED_COLS = 6

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        total = 0
        kept = 0
        skipped = 0

        for row in reader:
            total += 1
            if len(row) == EXPECTED_COLS:
                writer.writerow(row)
                kept += 1
            else:
                print(f"⚠️ Skipped malformed row {total}: {row}")
                skipped += 1

    print(f"\nCleaned CSV written to {OUTPUT_FILE}")
    print(f"Rows processed: {total} | Kept: {kept} | Skipped: {skipped}")

if __name__ == "__main__":
    main()
