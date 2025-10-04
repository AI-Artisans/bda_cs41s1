import pandas as pd

# Load dataset (adjust path if needed)
file_path = "./20251004 - dataset - Wk11.csv"
df = pd.read_csv(file_path)

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
