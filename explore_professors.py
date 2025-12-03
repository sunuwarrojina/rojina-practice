import pandas as pd

df = pd.read_csv("ku_star_professors_clean.csv")

print("Total rows (labs/professors):", len(df))
print("\nUnique Fields and counts:")
print(df["Field"].value_counts())

print("\nFirst 10 rows:")
print(df.head(10))
