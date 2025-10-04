import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")

# -----------------------------
# Step 0: Set dataset path
# -----------------------------
# Use local path if running on PC
# Use Kaggle path if running in Kaggle notebook
# Example: local -> "Customer_support_data.csv"
#          Kaggle -> "/kaggle/input/ecommerce-customer-service-satisfaction/Customer_support_data.csv"
DATA_PATH = "Customer_support_data.csv"  # <-- update this if file is in a subfolder

# -----------------------------
# Step 1: Load dataset
# -----------------------------
try:
    df = pd.read_csv(DATA_PATH)
    print(f"✅ Dataset loaded successfully from: {DATA_PATH}")
except FileNotFoundError:
    print(f"❌ File not found at {DATA_PATH}. Please check the path.")

# -----------------------------
# Step 2: Drop unnecessary columns
# -----------------------------
df_cleaned = df.drop(["Customer Remarks", "Order_id", "order_date_time"], axis=1)

# -----------------------------
# Step 3: Impute missing values
# -----------------------------
# Numerical features
numerical_cols = ["Item_price", "connected_handling_time"]
for col in numerical_cols:
    df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)

# Categorical features
categorical_cols = ["Customer_City", "Product_category"]
for col in categorical_cols:
    df_cleaned[col].fillna("Unknown", inplace=True)

# -----------------------------
# Step 4: Convert timestamp columns to datetime
# -----------------------------
timestamp_cols = ["Issue_reported at", "issue_responded", "Survey_response_Date"]
for col in timestamp_cols:
    df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce')

# -----------------------------
# Step 5: Impute missing datetime values
# -----------------------------
for col in ["Issue_reported at", "issue_responded"]:
    if df_cleaned[col].isna().sum() > 0:
        median_timestamp = pd.to_datetime(df_cleaned[col].dropna().astype(np.int64).median())
        df_cleaned[col].fillna(median_timestamp, inplace=True)

# -----------------------------
# Step 6: Encode categorical features
# -----------------------------
le = LabelEncoder()
for col in categorical_cols + ["Customer_Segment"]:
    if col in df_cleaned.columns:
        df_cleaned[col] = le.fit_transform(df_cleaned[col])

# -----------------------------
# Step 7: Final cleaned dataset
# -----------------------------
print("✅ Cleaning completed. Sample of cleaned dataset:")
print(df_cleaned.head())

# Optionally save cleaned dataset
df_cleaned.to_csv("Customer_support_data_cleaned.csv", index=False)
