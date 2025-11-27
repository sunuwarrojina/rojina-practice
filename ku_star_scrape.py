import requests
import pdfplumber
import pandas as pd

PDF_URL = "https://www.kugd.k.kyoto-u.ac.jp/wp-content/uploads/2025/11/Appendix-KU-STAR-Program-Laboratory-List_as-of-20251028"
PDF_PATH = "ku_star_labs.pdf"


def download_pdf():
    print(f"Downloading PDF from {PDF_URL} ...")
    response = requests.get(PDF_URL)
    response.raise_for_status()  # will crash if download fails

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
                    if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                        continue
                    rows.append(row)

    print(f"Total rows extracted: {len(rows)}")

    # Put into a DataFrame and save to CSV
    df = pd.DataFrame(rows)
    df.to_csv("ku_star_labs_raw.csv", index=False)
    print("Saved raw table to ku_star_labs_raw.csv")

    # Show just the first few lines in the console
    print("\nFirst 5 rows:")
    print(df.head())


def main():
    download_pdf()
    extract_tables()


if __name__ == "__main__":
    main()
