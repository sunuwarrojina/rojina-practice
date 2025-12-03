import requests
import pdfplumber
import pandas as pd

PDF_URL = "https://www.kugd.k.kyoto-u.ac.jp/wp-content/uploads/2025/11/Appendix-KU-STAR-Program-Laboratory-List_as-of-20251028"
PDF_PATH = "ku_star_labs.pdf"
RAW_CSV = "ku_star_labs_raw.csv"
CLEAN_CSV = "ku_star_professors_clean.csv"


def download_pdf():
    print(f"Downloading PDF from {PDF_URL} ...")
    response = requests.get(PDF_URL)
    response.raise_for_status()  # crash if download fails

    with open(PDF_PATH, "wb") as f:
        f.write(response.content)

    print(f"Saved PDF as {PDF_PATH}")


def extract_tables():
    print(f"Opening {PDF_PATH} ...")
    rows = []

    with pdfplumber.open(PDF_PATH) as pdf:
        print("Number of pages:", len(pdf.pages))

        for page_number, page in enumerate(pdf.pages, start=1):
            print(f"Extracting tables from page {page_number}...")
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    # skip completely empty rows
                    if not row or all(
                        cell is None or str(cell).strip() == "" for cell in row
                    ):
                        continue
                    rows.append(row)

    print(f"Total rows extracted: {len(rows)}")

    df = pd.DataFrame(rows)
    df.to_csv(RAW_CSV, index=False)
    print(f"Saved raw table to {RAW_CSV}")

    print("\nFirst 5 raw rows:")
    print(df.head())


def clean_data():
    print("\nCleaning data...")

    # Load without using any row as header
    df_raw = pd.read_csv(RAW_CSV, header=None)

    # Row 1 (index 1) contains the real column names: "No", "Field", "Name", ...
    header = df_raw.iloc[1].tolist()

    # Data starts from row 2 (index 2) – skip the first two rows
    df = df_raw.iloc[2:].copy()
    df.columns = header  # set proper column names

    # Keep only rows that have a real "No" value (start of each professor row)
    df = df[df["No"].notna() & (df["No"] != "No")] 

    # Drop any rows where "Name" is missing, just to be safe
    df = df[df["Name"].notna()]

    # Select the columns we care about
    columns_we_want = [
        "No",
        "Field",
        "Name",
        "Affiliation",
        "Research Topic",
        "Keywords",
        "Webpages",
        "Campus",
    ]
    df_clean = df[columns_we_want].copy()

    # Strip whitespace/newlines from all string cells
    df_clean = df_clean.applymap(
        lambda x: str(x).replace("\n", " ").strip() if isinstance(x, str) else x
    )

    df_clean.to_csv(CLEAN_CSV, index=False)
    print(f"Saved clean professor data to {CLEAN_CSV}")

    print("\nFirst 10 clean rows:")
    print(df_clean.head(10))


def main():
    download_pdf()
    extract_tables()
    clean_data()


if __name__ == "__main__":
    main()
