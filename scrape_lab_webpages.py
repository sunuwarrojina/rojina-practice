import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

INPUT_CSV = "ku_star_professors_clean.csv"
OUTPUT_CSV = "ku_star_professors_enriched.csv"

# Be polite: identify your script in User-Agent
HEADERS = {
    "User-Agent": "KU-STAR-ProfScraper/1.0 (contact: your_email@example.com)"
}


def normalize_url(url: str) -> str:
    """
    Clean up the URL a bit:
    - strip spaces
    - remove internal spaces
    - add https:// if missing
    """
    if not isinstance(url, str):
        return ""
    url = url.strip()
    # Remove spaces that came from PDF line breaks like "k yoto- u.ac.jp"
    url = url.replace(" ", "")
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def extract_email(soup: BeautifulSoup) -> str:
    """
    Try to find the first email on the page via mailto: links.
    This is heuristic and may not always work.
    """
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            return href.replace("mailto:", "").strip()
    return ""


def extract_snippet(soup: BeautifulSoup, max_chars: int = 300) -> str:
    """
    Get a rough text snippet from the page (first N characters of visible text).
    """
    # Remove script/style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    if not text:
        return ""
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


def scrape_lab_pages(df: pd.DataFrame, delay_seconds: float = 1.0) -> pd.DataFrame:
    """
    For each professor lab webpage, try to fetch the page and extract:
    - cleaned URL
    - HTTP status
    - page title
    - first email (if any)
    - short snippet of text
    """

    # Create new columns with default values
    df["LabURLOriginal"] = df["Webpages"]
    df["LabURLClean"] = ""
    df["LabHTTPStatus"] = pd.NA
    df["LabError"] = ""
    df["LabTitle"] = ""
    df["LabEmail"] = ""
    df["LabSnippet"] = ""

    for idx, row in df.iterrows():
        no_value = row["No"]

        # Skip the extra header-like row where No == "No"
        if isinstance(no_value, str) and no_value.strip() == "No":
            continue

        url_raw = row["Webpages"]
        if pd.isna(url_raw) or str(url_raw).strip() == "":
            # No URL available
            continue

        url_clean = normalize_url(str(url_raw))
        df.at[idx, "LabURLClean"] = url_clean

        if not url_clean:
            df.at[idx, "LabError"] = "Empty or invalid URL after cleaning"
            continue

        print(f"[{idx}] Fetching: {url_clean}")
        try:
            resp = requests.get(url_clean, headers=HEADERS, timeout=10)
            df.at[idx, "LabHTTPStatus"] = resp.status_code

            if resp.status_code != 200:
                df.at[idx, "LabError"] = f"HTTP {resp.status_code}"
                # Still continue to next; no parsing
                time.sleep(delay_seconds)
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Title
            title_tag = soup.find("title")
            if title_tag and title_tag.get_text(strip=True):
                df.at[idx, "LabTitle"] = title_tag.get_text(strip=True)

            # Email (if any)
            email = extract_email(soup)
            if email:
                df.at[idx, "LabEmail"] = email

            # Text snippet
            snippet = extract_snippet(soup)
            if snippet:
                df.at[idx, "LabSnippet"] = snippet

        except Exception as e:
            df.at[idx, "LabError"] = f"Exception: {type(e).__name__}: {e}"

        # Be polite to servers
        time.sleep(delay_seconds)

    return df


def main():
    print(f"Loading CSV: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)

    print("Original shape:", df.shape)

    df_enriched = scrape_lab_pages(df, delay_seconds=1.0)

    df_enriched.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved enriched dataset to {OUTPUT_CSV}")

    print("\nPreview of enriched columns:")
    cols_to_show = [
        "No",
        "Field",
        "Name",
        "LabURLOriginal",
        "LabURLClean",
        "LabHTTPStatus",
        "LabTitle",
        "LabEmail",
    ]
    print(df_enriched[cols_to_show].head(15))


if __name__ == "__main__":
    main()
    
