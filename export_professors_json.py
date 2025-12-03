import pandas as pd

CSV_PATH = "ku_star_professors_enriched.csv"
JSON_PATH = "ku_star_professors.json"


def load_data(csv_path: str) -> pd.DataFrame:
    print(f"Loading data from {csv_path} ...")
    df = pd.read_csv(csv_path)

    # Normalize text-like columns to avoid NaN showing up as "nan" strings
    text_cols = [
        "Field",
        "Name",
        "Affiliation",
        "Research Topic",
        "Keywords",
        "Campus",
        "LabURLOriginal",
        "LabURLClean",
        "LabTitle",
        "LabEmail",
        "LabSnippet",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).replace("nan", "").fillna("")

    return df


def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only the columns that are meaningful for JSON export.
    If some columns are missing, we just skip them safely.
    """
    desired_cols = [
        "No",
        "Field",
        "Name",
        "Affiliation",
        "Research Topic",
        "Keywords",
        "Campus",
        "LabURLOriginal",
        "LabURLClean",
        "LabHTTPStatus",
        "LabError",
        "LabTitle",
        "LabEmail",
        "LabSnippet",
    ]

    cols_present = [c for c in desired_cols if c in df.columns]
    df_out = df[cols_present].copy()

    # Optional: make sure IDs (No) are ints where possible
    if "No" in df_out.columns:
        # Some rows might be "No" header strings, drop them
        df_out = df_out[df_out["No"].astype(str) != "No"]
        # Try to convert to numeric safely
        df_out["No"] = pd.to_numeric(df_out["No"], errors="coerce")

    return df_out


def export_to_json(df: pd.DataFrame, json_path: str):
    """
    Export the DataFrame to a JSON file as a list of objects.
    """
    # Convert NaN to None in JSON
    df = df.where(pd.notnull(df), None)

    print(f"Exporting {len(df)} records to {json_path} ...")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)
    print(f"Done. JSON saved to {json_path}")


def main():
    df = load_data(CSV_PATH)
    df = select_columns(df)

    print("\nPreview of first 3 records that will go to JSON:")
    print(df.head(3))

    export_to_json(df, JSON_PATH)


if __name__ == "__main__":
    main()
