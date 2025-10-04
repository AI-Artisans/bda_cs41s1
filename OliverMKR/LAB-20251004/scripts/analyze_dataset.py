import pandas as pd
import csv

# Input/Output files
raw_file = "./20251004 - dataset - Wk11.csv"
cleaned_file = "./20251004_dataset_cleaned.csv"

# --- STEP 1: CLEAN THE DATASET FOR WEKA ---
with open(raw_file, "r", encoding="utf-8", errors="ignore") as infile, \
     open(cleaned_file, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)

    for row in reader:
        # Skip empty or malformed rows
        if not row or len(row) < 5:
            continue

        cleaned_row = []
        for field in row:
            if field is None:
                cleaned_row.append("")
            else:
                # Escape embedded quotes properly
                fixed = field.replace('"', '""')
                cleaned_row.append(fixed)

        # Ensure exactly 20 columns (truncate or pad with blanks)
        if len(cleaned_row) > 20:
            cleaned_row = cleaned_row[:20]
        elif len(cleaned_row) < 20:
            cleaned_row += [""] * (20 - len(cleaned_row))

        writer.writerow(cleaned_row)

print(f"✅ Cleaned dataset saved as: {cleaned_file}\n")

# --- STEP 2: LOAD CLEANED FILE INTO PANDAS FOR ANALYSIS ---
df = pd.read_csv(cleaned_file)

# 1. Dataset shape
print("Dataset Shape (rows, columns):", df.shape)

# 2. Data types
print("\n--- Column Data Types ---")
print(df.dtypes)

# 3. Missing values
print("\n--- Missing Values ---")
print(df.isnull().sum())

# 4. Sample unique values (first 5 for each column)
print("\n--- Sample Unique Values per Column ---")
for col in df.columns:
    print(f"\n{col} → {df[col].dropna().unique()[:5]}")

# 5. Basic statistics for numeric fields
print("\n--- Basic Statistics (Numeric Fields) ---")
print(df.describe())

# 6. Duplicate check
print("\n--- Duplicate Rows ---")
print("Number of duplicate rows:", df.duplicated().sum())

# 7. Class distribution (CSAT Score)
if "CSAT Score" in df.columns:
    print("\n--- CSAT Score Distribution ---")
    print(df["CSAT Score"].value_counts())
