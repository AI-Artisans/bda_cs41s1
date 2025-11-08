# Laboratory Submissions

This repository contains laboratory outputs for **Big Data Analytics**.  
All submissions are organized by lab activity folders.

---

## Lab-20250806
Contains outputs for **Lab Activity 01: Understanding Data Characteristics and Quality**.  
- Notes and analysis on data attributes, data quality issues, and dataset exploration.
- **Files:**
  - `index.html` - HTML documentation of the analysis

---

## Lab-20250913
Contains outputs for **Lab Activity 03: CRISP-DM | Exploring CRISP-DM Phases 1, 2, & 3 using Bank Marketing Data**.  

### Files:
- **bank_marketing_cleaned.xlsx**  
  Contains initial vs. final summaries for the *Job, Marital, Education,* and *Contact* attributes.  
  - Sheet 1: Initial Summary (raw categories with inconsistencies).  
  - Sheet 2: Final Summary (after standardization and clean-up).  

- **20250913-Laboratory.sql**  
  MySQL database dump containing the restored `bank_marketing` table.  

### Notes
- All data cleaning and preparation steps were documented in SQL queries.  
- This folder demonstrates the **CRISP-DM phases of Business Understanding, Data Understanding, and Data Preparation** using the Bank Marketing dataset.

---

## Lab-20250920
Contains datasets for **Lab Activity: Introduction to ARFF Format and WEKA**.  
- **Files:**
  - `diabetes.arff` - Diabetes dataset in ARFF format
  - `iris.arff` - Iris dataset in ARFF format
- **Purpose:** Familiarization with ARFF (Attribute-Relation File Format) used by WEKA machine learning toolkit.

---

## Lab-20250927
Contains outputs for **Lab Activity: Telco Customer Churn Analysis**.  
- **Files:**
  - `Telco_Cusomer_Churn.arff` - Telco Customer Churn dataset in ARFF format
  - `Telco_Cusomer_Churn.csv` - Telco Customer Churn dataset in CSV format
- **Purpose:** Analysis of customer churn data for telecommunications company.

---

## Lab-20251004
Contains outputs for **Lab Activity: Customer Support CSAT Analysis (Week 11)**.  
This lab focuses on analyzing customer support satisfaction (CSAT) using classification algorithms in WEKA.

### Files:
- **data/**
  - `20251004 - dataset - Wk11.csv` - Raw dataset
  - `20251004 - dataset - Wk11 - cleaned.csv` - Cleaned dataset for modeling
- **models/**
  - `ZeroR_20251004_dataset_Wk11.model` - Saved WEKA model (best performing with 69.4% accuracy)
- **scripts/**
  - `clean_dataset.py` - Python script to clean the raw CSV for WEKA compatibility
  - `analyze_dataset.py` - Python script for exploratory data analysis
- **sql/**
  - `lab_wk11.sql` - SQL queries for data preparation
- **README.md** - Detailed documentation for this lab

### Key Highlights:
- **Target Attribute:** CSAT Score
- **Algorithms Tested:** Naive Bayes, Decision Stump, ZeroR
- **Best Model:** ZeroR (69.4% correctly classified instances)
- **Note:** Dataset is highly imbalanced, with most algorithms predicting the majority class

---

## Lab-20251025
Contains outputs for **Lab Activity: Predictive Modeling (Week 12)**.  
- **Files:**
  - `20251025 - dataset - Wk12.csv` - Dataset for week 12
  - `20251025 - dataset - Wk12.sql` - SQL queries for data preparation
  - `LMT_BestModel_Wk12.model .model` - Saved WEKA model (LMT - Logistic Model Trees)
- **Purpose:** Advanced predictive modeling using LMT algorithm.

---

## Lab-20251108
Contains outputs for **Lab Activity: Model Evaluation and Testing**.  
- **Files:**
  - `iris.arff` - Iris dataset (training)
  - `iris_test.arff` - Iris test dataset
  - `weather_nominal_training.arff` - Weather nominal training dataset
  - `weather_nominal_test.arff` - Weather nominal test dataset
- **Purpose:** Practice with train-test split and model evaluation using separate training and test datasets.

---

## Repository Structure
```
OliverMKR/
├── LAB-20250806/          # Lab 01: Data Characteristics and Quality
├── LAB-20250913/          # Lab 03: CRISP-DM Phases 1-3
├── LAB-20250920/          # ARFF Format Introduction
├── LAB-20250927/          # Telco Customer Churn Analysis
├── LAB-20251004/          # CSAT Analysis (Week 11)
├── LAB-20251025/          # Predictive Modeling (Week 12)
├── LAB-20251108/          # Model Evaluation and Testing
└── README.md
```
