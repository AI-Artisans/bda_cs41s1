import pandas as pd
import numpy as np

df = pd.read_csv("ecommerce_customer_service_satisfaction.csv")

# ---------- 0) Helpers ----------
NULL_STRINGS = {"", "nan", "NaN", "None", "NULL", "null"}

def clean_text_col(s: pd.Series) -> pd.Series:
    """
    Clean a textual column while preserving true NaN.
    Uses pandas' StringDtype so NA stays NA, not the literal 'nan'.
    Also converts common null-like strings back to NA.
    """
    s = s.astype("string")                       # keep <NA>, not 'nan'
    s = s.str.strip().str.replace(r"\s+", " ", regex=True)
    s = s.mask(s.str.lower().isin(NULL_STRINGS)) # back to <NA> if 'nan','', etc.
    return s

def parse_with_formats(s: pd.Series, formats, dayfirst=False) -> pd.Series:
    """Try explicit formats first; fallback to flexible parser with chosen dayfirst."""
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    s_str = s.astype("string")
    for fmt in formats:
        parsed = pd.to_datetime(s_str, format=fmt, errors="coerce")
        out = out.fillna(parsed)  # keep existing successes; fill new successes
    # Fallback for leftovers
    need_fallback = out.isna()
    if need_fallback.any():
        out.loc[need_fallback] = pd.to_datetime(
            s_str.loc[need_fallback],
            errors="coerce",
            dayfirst=dayfirst
        )
    return out

# ---------- 1) Text columns (preserve NaN) ----------
text_cols = [
    'Unique id','channel_name','category','Sub-category','Customer Remarks',
    'Order_id','Customer_City','Product_category','Agent_name','Supervisor',
    'Manager','Tenure Bucket','Agent Shift'
]
for c in text_cols:
    if c in df.columns:
        df[c] = clean_text_col(df[c])

# ---------- 2) Datetime parsing (explicit + fallback) ----------
date_cols = ["order_date_time","Issue_reported at","issue_responded","Survey_response_Date"]

# If you saw %d/%m/%Y %H:%M in the warning, include it.
fmt_map = {
    "order_date_time":      ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M", "%Y-%m-%d"],
    "Issue_reported at":    ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M"],
    "issue_responded":      ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M"],
    "Survey_response_Date": ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M", "%Y-%m-%d"]
}

for c in date_cols:
    if c in df.columns:
        # dayfirst=True because we saw a dd/mm pattern in your warning
        df[c] = parse_with_formats(df[c], fmt_map.get(c, []), dayfirst=True)

# ---------- 3) Interval features with sanity (no negatives) ----------
def minutes(a, b):
    delta = (a - b).dt.total_seconds() / 60.0
    out = pd.to_numeric(delta, errors="coerce")
    out[(out < 0) | ~np.isfinite(out)] = np.nan
    return out

df["wait_minutes"] = minutes(df["issue_responded"], df["Issue_reported at"])
df["order_to_issue_minutes"] = minutes(df["Issue_reported at"], df["order_date_time"])

# ---------- 4) Target ----------
df["high_csat"] = (df["CSAT Score"] >= 4).astype("int8")

# ---------- 5) Numeric outliers -> NaN then impute ----------
num_cols = ["Item_price","connected_handling_time","wait_minutes","order_to_issue_minutes"]
for c in num_cols:
    if c in df.columns:
        x = pd.to_numeric(df[c], errors="coerce")
        q1, q3 = x.quantile(0.25), x.quantile(0.75)
        iqr = q3 - q1
        lo = max(0, q1 - 1.5*iqr)     # durations/price shouldn't be negative
        hi = q3 + 3*iqr
        x = x.mask((x < lo) | (x > hi))
        df[c] = x

df["log_item_price"] = np.log1p(pd.to_numeric(df["Item_price"], errors="coerce"))

# ---------- 6) Now fill missings (order matters!) ----------
# Categorical → 'Unknown' (after fixing stringified nulls)
for c in text_cols:
    if c in df.columns:
        df[c] = df[c].fillna("Unknown")

# Numeric → median
for c in num_cols + ["log_item_price"]:
    if c in df.columns:
        df[c] = df[c].fillna(df[c].median())

# ---------- 7) Collapse rare levels ----------
def collapse_rare(series, min_frac=0.01):
    vc = series.value_counts(normalize=True, dropna=False)
    kept = set(vc[vc >= min_frac].index)
    return series.where(series.isin(kept), other="Other")

for c in ["Customer_City","Sub-category","Product_category","Agent_name","Supervisor","Manager"]:
    if c in df.columns:
        df[c] = collapse_rare(df[c], min_frac=0.01)

# ---------- 8) Final modeling view ----------
model_cols = [
    "high_csat","wait_minutes","order_to_issue_minutes","connected_handling_time",
    "log_item_price","channel_name","category","Sub-category","Product_category",
    "Agent Shift","Tenure Bucket","Customer_City"
]
df_model = df[[c for c in model_cols if c in df.columns]].copy()

print(df_model.head(3))
print(df_model.isna().sum())
print(df_model["high_csat"].value_counts(normalize=True).rename({0:"NO",1:"YES"}))

import re

date_cols = ["order_date_time","Issue_reported at","issue_responded","Survey_response_Date"]

# Step A: collect raw (pre-parsed) strings
raw_dates = {}
for c in date_cols:
    if c in df.columns:
        s = df[c].astype("string")
        raw_dates[c] = s

# Step B: simple regex-based format tagging
patterns = [
    ("ymd_hms_dash",   re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")),  # 2024-07-21 14:05:30
    ("ymd_hm_dash",    re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")),        # 2024-07-21 14:05
    ("ymd_dash",       re.compile(r"^\d{4}-\d{2}-\d{2}$")),                    # 2024-07-21
    ("dmy_hm_slash",   re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}$")),  # 21/07/2024 14:05
    ("mdy_hm_slash",   re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}$")),  # 07/21/2024 14:05 (ambig by text only)
    ("dmy_hms_slash",  re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2}$")), # 21/07/2024 14:05:30
    ("mdy_hms_slash",  re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2}$")), # 07/21/2024 14:05:30
]

fmt_map = {
    "ymd_hms_dash":  ("%Y-%m-%d %H:%M:%S", False),
    "ymd_hm_dash":   ("%Y-%m-%d %H:%M",    False),
    "ymd_dash":      ("%Y-%m-%d",          False),
    "dmy_hm_slash":  ("%d/%m/%Y %H:%M",    True),
    "mdy_hm_slash":  ("%m/%d/%Y %H:%M",    False),
    "dmy_hms_slash": ("%d/%m/%Y %H:%M:%S", True),
    "mdy_hms_slash": ("%m/%d/%Y %H:%M:%S", False),
}

def strict_parse_series(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    # classify each row
    tag = pd.Series("unknown", index=s.index, dtype="string")
    for name, rgx in patterns:
        tag = tag.mask(tag.eq("unknown") & s.fillna("").str.fullmatch(rgx), other=name)
    # parse per tag
    for name, (fmt, _dayfirst) in fmt_map.items():
        m = tag.eq(name)
        if m.any():
            out.loc[m] = pd.to_datetime(s.loc[m], format=fmt, errors="coerce")
    # anything still unknown remains NaT; we report it below
    return out, tag

# Apply per column and report
for c in date_cols:
    if c in raw_dates:
        parsed_c, tag = strict_parse_series(raw_dates[c])
        df[c] = parsed_c  # overwrite with strict parse (no fuzzy fallback)
        counts = tag.value_counts(dropna=False).to_dict()
        unknown_examples = raw_dates[c][tag.eq("unknown")].dropna().unique()[:5]
        print(f"[{c}] format counts:", counts)
        if len(unknown_examples):
            print(f"[{c}] unknown examples (first 5):", list(unknown_examples))

# Optional: simple leakage check — any single level dominating?
for col in ["Agent_name","Supervisor","Manager","Agent Shift","Tenure Bucket","Customer_City"]:
    if col in df_model.columns:
        m = df_model.groupby(col)["high_csat"].mean().sort_values(ascending=False)
        print(col, "peak mean:", m.head(3).to_dict())

# Export for WEKA
df_model.to_csv("model_ready_csat.csv", index=False)
print("Wrote model_ready_csat.csv")
