# KU-STAR Professor Data Scraper & Lab Explorer

This project builds a small data pipeline and search tool for the
**Kyoto University KU-STAR Program** laboratory list.

The goal is to:
1. Scrape professor / lab information from the official KU-STAR PDF.
2. Clean and structure the data into a CSV dataset.
3. Visit each lab website (when a URL is available) and enrich the data
   with page titles, text snippets, and basic metadata.
4. Provide an interactive search tool so students can find labs by field,
   campus, or research keywords and export the results.

---

## Project Structure

- `ku_star_scrape.py`  
  Downloads the KU-STAR PDF, extracts tables with `pdfplumber`, and
  builds a clean CSV:

  - Input: official KU-STAR PDF
  - Output: `ku_star_professors_clean.csv`

- `scrape_lab_webpages.py`  
  Reads `ku_star_professors_clean.csv`, visits each lab URL with `requests`
  and `BeautifulSoup`, and enriches the dataset:

  - Adds columns: `LabURLClean`, `LabHTTPStatus`, `LabTitle`, `LabEmail`, `LabSnippet`
  - Output: `ku_star_professors_enriched.csv`

- `explore_professors.py`  
  Simple script to inspect and summarize the dataset (rows, fields, campuses).

- `search_labs.py`  
  Interactive CLI tool that:
  - Searches labs by **Field**, **Campus**, or **Keyword**
  - Shows results in the terminal
  - Can **save the current search results to a CSV file** for further analysis

---

## Setup

```bash
# Create and activate virtual environment (already done once)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
