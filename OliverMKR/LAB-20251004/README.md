# LAB-20251004 – Customer Support CSAT Analysis

## Overview
This lab focuses on analyzing customer support satisfaction (CSAT) using a sample dataset. The project includes **data cleaning, exploratory analysis, and predictive modeling** using WEKA.

The target attribute is **CSAT Score**, which is predicted using classification algorithms.

---

## Folder Structure
```
LAB-20251004/
├── data/
│   ├── 20251004 - dataset - Wk11.csv                 # Raw dataset
│   └── 20251004 - dataset - Wk11 - cleaned.csv       # Cleaned dataset for modeling
├── models/
│   └── ZeroR_20251004_dataset_Wk11.model             # Saved WEKA model
├── scripts/
│   ├── clean_dataset.py                              # Python script to clean the raw CSV
│   └── analyze_dataset.py                            # Python script for exploratory analysis
├── sql/
│   └── lab_wk11.sql                                  # Optional SQL queries
└── README.md
```

---

## Dataset

- **Raw Dataset:** `20251004 - dataset - Wk11.csv`
- **Cleaned Dataset:** `20251004 - dataset - Wk11 - cleaned.csv`
- **Columns include:**
  - Unique_id, channel_name, category, Sub-category, Issue_reported_at, issue_responded, Survey_response_Date, Customer_City, Product_category, Item_price, connected_handling_time, Agent_name, Supervisor, Manager, Tenure_Bucket, Agent_Shift, CSAT_Score

---

## Scripts

### 1. **clean_dataset.py**
- Loads raw CSV and performs cleaning:
  - Escapes quotes
  - Ensures all fields are properly quoted for WEKA compatibility
- Saves cleaned CSV to `data/` directory

### 2. **analyze_dataset.py**
- Loads cleaned CSV
- Performs exploratory data analysis (EDA)
- Prepares data for modeling (imputation, type conversion)

---

## Modeling

- **Target Attribute:** `CSAT_Score`
- **Classification Algorithms Tested in WEKA:**
  1. **Naive Bayes**
  2. **Decision Stump**
  3. **ZeroR**

- **Best Performing Model:** `ZeroR_20251004_dataset_Wk11.model`
  - Achieved **69.4% correctly classified instances**
  - Stored in `models/` folder for future use in WEKA

---

## Usage Instructions

### Running Python Scripts

```bash
# Clean the dataset
python scripts/clean_dataset.py

# Analyze the cleaned dataset
python scripts/analyze_dataset.py
```

### Using the WEKA Model

1. Open WEKA Explorer
2. Load `data/20251004 - dataset - Wk11 - cleaned.csv`
3. Go to **Classify** tab → **Open model** → Load `models/ZeroR_20251004_dataset_Wk11.model`
4. Evaluate or make predictions on new data

---

## Notes

- Dataset is highly imbalanced → most algorithms predict majority class (CSAT_Score = 5)
- Decision Stump and ZeroR are memory-efficient for large datasets
- Naive Bayes can predict minority classes but with lower overall accuracy
- Column names have been standardized (spaces replaced with underscores for consistency)

---

## Key Findings

- ZeroR model achieved the highest accuracy (69.4%) due to class imbalance
- The dataset requires additional preprocessing for better minority class prediction
- Consider techniques like SMOTE or class weighting for future model improvements