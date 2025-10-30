import pandas as pd
import numpy as np

# === Load Dataset ===
df = pd.read_csv("20251025 - dataset - Wk12.csv")

print(f"Analyzing {df.shape[1]} total columns ({df.shape[0]} rows).\n")

def analyze_all_columns(df, rare_threshold=0.01):
    total_rows = len(df)
    summary = []

    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)

        missing = series.isna().sum()
        empty = (series.astype(str).str.strip() == "").sum() if series.dtype == "object" else 0
        nunique = series.nunique(dropna=True)
        top_vals = series.value_counts(dropna=False).head(5).to_dict()

        # Case inconsistencies (only for object columns)
        case_inconsistency = False
        if series.dtype == "object":
            lower_set = {x.lower() for x in series.dropna().astype(str)}
            case_inconsistency = len(lower_set) != nunique

        # Rare values detection (only for categorical-like)
        rare_count = 0
        if nunique > 1 and nunique < total_rows / 2:  # only meaningful for discrete columns
            freqs = series.value_counts(normalize=True, dropna=True)
            rare_count = (freqs < rare_threshold).sum()

        summary.append({
            "Column": col,
            "Data Type": dtype,
            "Unique Values": nunique,
            "Missing": missing,
            "Empty Strings": empty,
            "Case Inconsistent": case_inconsistency,
            "Rare Categories (<1%)": rare_count,
            "Top 5 Values": "; ".join([f"{k}: {v}" for k, v in top_vals.items()])
        })

    return pd.DataFrame(summary)

# === Run analysis ===
full_summary = analyze_all_columns(df)

# === Save to CSV ===
full_summary.to_csv("dataset_sanitation_report.csv", index=False)

# === Flag potential issues ===
issues = full_summary[
    (full_summary["Missing"] > 0) |
    (full_summary["Empty Strings"] > 0) |
    (full_summary["Case Inconsistent"]) |
    (full_summary["Rare Categories (<1%)"] > 0)
]

print("✅ Reports saved:")
print(" - dataset_sanitation_report.csv (all columns)")
