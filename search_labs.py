import pandas as pd

CSV_PATH = "ku_star_professors_enriched.csv"


def load_data():
    print(f"Loading data from {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)

    # Normalize text columns to avoid NaN issues
    text_cols = [
        "Field",
        "Name",
        "Affiliation",
        "Research Topic",
        "Keywords",
        "Campus",
        "LabSnippet",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("")

    # If LabURLClean is missing, fall back to LabURLOriginal
    if "LabURLClean" not in df.columns and "LabURLOriginal" in df.columns:
        df["LabURLClean"] = df["LabURLOriginal"].fillna("")

    return df


def show_basic_stats(df: pd.DataFrame):
    print("\n=== Dataset Overview ===")
    print("Total labs/professors:", len(df))
    if "Field" in df.columns:
        print("\nLabs per Field:")
        print(df["Field"].value_counts())
    if "Campus" in df.columns:
        print("\nLabs per Campus:")
        print(df["Campus"].value_counts())


def show_results(results: pd.DataFrame, max_rows: int = 15) -> pd.DataFrame:
    """
    Print a preview of the results and return the full results DataFrame.
    """
    if results.empty:
        print("No results.\n")
        return results

    results_to_show = results.head(max_rows)

    cols = [
        "No",
        "Field",
        "Name",
        "Affiliation",
        "Campus",
        "LabURLClean",
        "LabTitle",
        "LabEmail",
    ]
    # Keep only columns that actually exist
    cols = [c for c in cols if c in results_to_show.columns]

    print()
    print(results_to_show[cols].to_string(index=False))
    print(f"\n(Showing up to {max_rows} results.)\n")

    return results


def save_results_to_csv(results: pd.DataFrame, default_name: str):
    """
    Ask the user if they want to save the given results DataFrame to CSV.
    """
    if results is None or results.empty:
        print("No results to save.\n")
        return

    choice = input(f"Save these {len(results)} results to CSV? (y/n): ").strip().lower()
    if choice != "y":
        return

    filename = input(f"Enter filename (or press Enter for '{default_name}'): ").strip()
    if not filename:
        filename = default_name

    if not filename.endswith(".csv"):
        filename += ".csv"

    results.to_csv(filename, index=False)
    print(f"Saved {len(results)} results to {filename}\n")


def search_by_field(df: pd.DataFrame, field_query: str):
    field_query = field_query.strip().lower()
    if not field_query:
        print("Empty field query.\n")
        return

    mask = df["Field"].str.lower().str.contains(field_query)
    results = df[mask]
    print(f"\nFound {len(results)} labs for field containing '{field_query}':")
    results = show_results(results)
    save_results_to_csv(results, default_name="labs_by_field")


def search_by_campus(df: pd.DataFrame, campus_query: str):
    if "Campus" not in df.columns:
        print("No Campus column in dataset.\n")
        return

    campus_query = campus_query.strip().lower()
    if not campus_query:
        print("Empty campus query.\n")
        return

    mask = df["Campus"].str.lower().str.contains(campus_query)
    results = df[mask]
    print(f"\nFound {len(results)} labs on campus containing '{campus_query}':")
    results = show_results(results)
    save_results_to_csv(results, default_name="labs_by_campus")


def search_by_keyword(df: pd.DataFrame, keyword_query: str):
    keyword_query = keyword_query.strip().lower()
    if not keyword_query:
        print("Empty keyword query.\n")
        return

    # Build a combined text field to search in
    combined = (
        df.get("Research Topic", pd.Series([""] * len(df))).astype(str).str.lower()
        + " "
        + df.get("Keywords", pd.Series([""] * len(df))).astype(str).str.lower()
        + " "
        + df.get("LabSnippet", pd.Series([""] * len(df))).astype(str).str.lower()
    )

    mask = combined.str.contains(keyword_query)
    results = df[mask]
    print(f"\nFound {len(results)} labs for keyword '{keyword_query}':")
    results = show_results(results)
    save_results_to_csv(results, default_name="labs_by_keyword")


def main():
    df = load_data()
    show_basic_stats(df)

    while True:
        print("\n=== KU-STAR Lab Search Menu ===")
        print("1. Search by Field (e.g., 'Informatics', 'Biological Sciences')")
        print("2. Search by Campus (e.g., 'Yoshida')")
        print("3. Search by Keyword (e.g., 'AI', 'energy', 'climate')")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            field_query = input("Enter field text to search: ")
            search_by_field(df, field_query)
        elif choice == "2":
            campus_query = input("Enter campus text to search: ")
            search_by_campus(df, campus_query)
        elif choice == "3":
            keyword_query = input(
                "Enter keyword to search in topics/keywords/snippets: "
            )
            search_by_keyword(df, keyword_query)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1–4.")


if __name__ == "__main__":
    main()
