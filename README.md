```markdown
# BookScout 🔍📚

**BookScout** is a full‑stack, AI‑powered book recommendation web app that uses semantic similarity, genre filtering, and automated metadata enrichment to suggest books you’ll love. Built with Flask, Pandas, BeautifulSoup, Hugging Face Transformers, and Chart.js, it features a dark‑mode UI and a scalable CSV‑backed cache.

---

## 🚀 Features

- **Search & Recommend**  
  - Query by book title  
  - TF‑IDF + cosine similarity on descriptions + genres  
  - Optional genre filter checkboxes  

- **Metadata Enrichment**  
  - Google Books API for base metadata  
  - Wikipedia fallback for plot summaries & categories  
  - Zero‑shot genre classification (facebook/bart‑large‑mnli)  

- **Bulk Addition**  
  - Scrape Goodreads lists for new titles  
  - Clean & dedupe titles (removes series info)  
  - Add in bulk via `bulk_add.py` with auto‑preprocessing  

- **Data Utilities** (`/scripts`)  
  - `scrape_goodreads.py` → Fetch new titles from Goodreads  
  - `strip_malformed_rows.py` → Clean up broken CSV rows  
  - `clean_categories.py` → Sanitize category fields  
  - `genre_counter.py` → Count & normalize genres (CSV + `<option>` HTML)  
  - `structure_maker.py` → Print project folder tree  

---




````
## ⚙️ Setup & Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yourusername/bookscout.git
   cd bookscout
````

2. **Create & activate virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   * Copy `.env.example` to `.env`
   * Add your `GOOGLE_BOOKS_API_KEY` (optional)

---

## 🏃‍♂️ Running the App

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

* Open [http://localhost:5000](http://localhost:5000)
* Enter a book title and optional genre filters → See recommendations!

---

## 🛠️ Bulk-Add Workflow

1. **Generate new titles** (optional)

   ```bash
   python scripts/scrape_goodreads.py
   ```
2. **Add to cache & preprocess**

   ```bash
   python bulk_add.py
   ```

---

## 📊 Data Analysis

* **Clean categories**:

  ```bash
  python scripts/clean_categories.py
  ```
* **Count genres & generate options**:

  ```bash
  python scripts/genre_counter.py
  ```

---

## 📦 Packaging & Deployment

* Dockerize with a `Dockerfile` (not included)
* Deploy to Heroku / AWS / GCP with `Procfile` & environment variables

---

## 🔗 Links & Resources

* [Google Books API](https://developers.google.com/books)
* [Hugging Face Transformers](https://huggingface.co/docs/transformers)
* [Chart.js](https://www.chartjs.org/)
* [Flask](https://flask.palletsprojects.com/)

---

## 👤 Author

**Dev Salot**
[GitHub](https://github.com/yourusername) • [Email](mailto:devsalot@gmail.com)

Feel free to fork, star, and contribute!

```
```
