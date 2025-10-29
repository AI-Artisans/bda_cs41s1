import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_CSV = r'C:\Users\A-224 (PC1)\Documents\VS Code\bda_cs41s1\PLACENCIAIKA\20251025-Lab-Wk12\20251025 - dataset - Wk12.csv'
OUTPUT_CSV = r'C:\Users\A-224 (PC1)\Documents\VS Code\bda_cs41s1\PLACENCIAIKA\20251025-Lab-Wk12\weka_ready_dataset.csv'

# ============================================================================
# PREPROCESSING FUNCTIONS
# ============================================================================

def load_csv_completely(file_path):
    """Load entire CSV file using chunk reading"""
    print(f"📂 Loading CSV from: {file_path}")
    
    # Count rows
    with open(file_path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for line in f) - 1
    
    print(f"📄 Total rows: {total_lines:,}")
    
    # Load in chunks
    chunks = []
    chunk_size = 10000
    
    for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size, encoding='utf-8', low_memory=False)):
        chunks.append(chunk)
        loaded = min((i + 1) * chunk_size, total_lines)
        print(f"   Loading: {loaded:,}/{total_lines:,} rows ({(loaded/total_lines)*100:.1f}%)")
    
    df = pd.concat(chunks, ignore_index=True)
    print(f"✓ Loaded {len(df):,} records\n")
    
    return df

def clean_for_weka(df):
    """Clean and transform dataset for WEKA compatibility"""
    
    print("🧹 Preprocessing for WEKA compatibility...\n")
    
    # Make a copy to avoid warnings
    df = df.copy()
    
    # ========================================================================
    # 1. HANDLE MISSING VALUES
    # ========================================================================
    print("1️⃣  Handling missing values...")
    
    # Replace empty strings with NaN first
    df.replace('', np.nan, inplace=True)
    df.replace('nan', np.nan, inplace=True)
    df.replace('NaN', np.nan, inplace=True)
    
    # For categorical fields, replace NaN with explicit category
    categorical_replacements = {
        'Malware Indicators': 'None',
        'Alerts/Warnings': 'No_Alert',
        'Protocol': 'Unknown',
        'Packet Type': 'Unknown',
        'Traffic Type': 'Unknown',
        'Attack Type': 'Unknown',
        'Attack Signature': 'Unknown',
        'Action Taken': 'Unknown',  # Critical for classification
        'Severity Level': 'Unknown',
        'Network Segment': 'Unknown',
        'Proxy Information': 'None',
        'Firewall Logs': 'None',
        'IDS/IPS Alerts': 'None',
        'Log Source': 'Unknown'
    }
    
    for col, value in categorical_replacements.items():
        if col in df.columns:
            df[col].fillna(value, inplace=True)
    
    print(f"   ✓ Categorical fields filled with default values")
    
    # ========================================================================
    # 2. REMOVE TEXT FIELDS (WEKA doesn't handle long text well)
    # ========================================================================
    print("\n2️⃣  Removing text fields unsuitable for WEKA...")
    
    text_fields_to_remove = [
        'Payload Data',  # Long text content
        'User Information',  # High cardinality names
        'Device Information',  # Very long user agent strings
        'Geo-location Data'  # Inconsistent format
    ]
    
    for field in text_fields_to_remove:
        if field in df.columns:
            df.drop(columns=[field], inplace=True)
            print(f"   ✗ Removed: {field}")
    
    # ========================================================================
    # 3. CONVERT TIMESTAMP TO NUMERIC FEATURES
    # ========================================================================
    print("\n3️⃣  Converting timestamp to numeric features...")
    
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        # Extract useful temporal features
        df['Year'] = df['Timestamp'].dt.year.fillna(0).astype(int)
        df['Month'] = df['Timestamp'].dt.month.fillna(0).astype(int)
        df['Day'] = df['Timestamp'].dt.day.fillna(0).astype(int)
        df['Hour'] = df['Timestamp'].dt.hour.fillna(0).astype(int)
        df['DayOfWeek'] = df['Timestamp'].dt.dayofweek.fillna(0).astype(int)
        
        # Drop original timestamp
        df.drop(columns=['Timestamp'], inplace=True)
        print(f"   ✓ Created: Year, Month, Day, Hour, DayOfWeek")
        print(f"   ✗ Removed: Timestamp")
    
    # ========================================================================
    # 4. CONVERT IP ADDRESSES TO NUMERIC
    # ========================================================================
    print("\n4️⃣  Converting IP addresses to numeric...")
    
    def ip_to_int(ip_str):
        """Convert IP address to integer"""
        try:
            if pd.isna(ip_str) or ip_str == '':
                return 0
            parts = str(ip_str).split('.')
            if len(parts) != 4:
                return 0
            return int(parts[0]) * 16777216 + int(parts[1]) * 65536 + int(parts[2]) * 256 + int(parts[3])
        except:
            return 0
    
    if 'Source IP Address' in df.columns:
        df['Source_IP_Numeric'] = df['Source IP Address'].apply(ip_to_int)
        df.drop(columns=['Source IP Address'], inplace=True)
        print(f"   ✓ Converted: Source IP Address → Source_IP_Numeric")
    
    if 'Destination IP Address' in df.columns:
        df['Dest_IP_Numeric'] = df['Destination IP Address'].apply(ip_to_int)
        df.drop(columns=['Destination IP Address'], inplace=True)
        print(f"   ✓ Converted: Destination IP Address → Dest_IP_Numeric")
    
    if 'Proxy Information' in df.columns:
        df['Proxy_IP_Numeric'] = df['Proxy Information'].apply(ip_to_int)
        df.drop(columns=['Proxy Information'], inplace=True)
        print(f"   ✓ Converted: Proxy Information → Proxy_IP_Numeric")
    
    # ========================================================================
    # 5. CLEAN NUMERIC FIELDS
    # ========================================================================
    print("\n5️⃣  Cleaning numeric fields...")
    
    numeric_fields = {
        'Source Port': 0,
        'Destination Port': 0,
        'Packet Length': 0,
        'Anomaly Scores': 0.0
    }
    
    for field, default_value in numeric_fields.items():
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(default_value)
            print(f"   ✓ Cleaned: {field}")
    
    # ========================================================================
    # 6. CLEAN CATEGORICAL FIELDS (Remove spaces, special chars)
    # ========================================================================
    print("\n6️⃣  Cleaning categorical fields...")
    
    categorical_fields = [
        'Protocol', 'Packet Type', 'Traffic Type', 'Malware Indicators',
        'Alerts/Warnings', 'Attack Type', 'Attack Signature', 'Action Taken',
        'Severity Level', 'Network Segment', 'Firewall Logs', 'IDS/IPS Alerts',
        'Log Source'
    ]
    
    for field in categorical_fields:
        if field in df.columns:
            # Remove spaces and special characters
            df[field] = df[field].astype(str).str.replace(' ', '_', regex=False)
            df[field] = df[field].str.replace('[^A-Za-z0-9_]', '', regex=True)
            df[field] = df[field].replace('', 'Unknown')
            print(f"   ✓ Cleaned: {field}")
    
    # ========================================================================
    # 7. RENAME COLUMNS (Remove spaces for WEKA compatibility)
    # ========================================================================
    print("\n7️⃣  Renaming columns...")
    
    df.columns = [col.replace(' ', '_').replace('/', '_').replace('-', '_') for col in df.columns]
    print(f"   ✓ All column names cleaned")
    
    # ========================================================================
    # 8. ENSURE CLASS LABEL IS LAST COLUMN (WEKA convention)
    # ========================================================================
    print("\n8️⃣  Moving class label to last column...")
    
    if 'Action_Taken' in df.columns:
        # Move Action_Taken to last position
        cols = [col for col in df.columns if col != 'Action_Taken']
        cols.append('Action_Taken')
        df = df[cols]
        print(f"   ✓ 'Action_Taken' moved to last column (WEKA class label)")
    
    # ========================================================================
    # 9. REMOVE ROWS WITH UNKNOWN CLASS LABEL
    # ========================================================================
    print("\n9️⃣  Filtering records with valid class labels...")
    
    if 'Action_Taken' in df.columns:
        before_count = len(df)
        df = df[df['Action_Taken'] != 'Unknown']
        after_count = len(df)
        removed = before_count - after_count
        print(f"   ✓ Kept {after_count:,} records with valid class labels")
        print(f"   ✗ Removed {removed:,} records with Unknown class")
    
    # ========================================================================
    # 10. FINAL DATA VALIDATION
    # ========================================================================
    print("\n🔍 Final validation...")
    
    print(f"   • Total records: {len(df):,}")
    print(f"   • Total features: {len(df.columns)}")
    print(f"   • Class label column: Action_Taken (position {df.columns.tolist().index('Action_Taken') + 1})")
    
    # Check for any remaining issues
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print(f"\n   ⚠️  Warning: Some columns still have NaN values:")
        for col, count in null_counts[null_counts > 0].items():
            print(f"      - {col}: {count:,} NaN values")
    else:
        print(f"   ✓ No NaN values remaining")
    
    return df

def save_weka_ready_csv(df, output_path):
    """Save preprocessed data to CSV"""
    print(f"\n💾 Saving WEKA-ready CSV to: {output_path}")
    
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✓ File saved successfully ({file_size:.2f} MB)")
    
    return True


def generate_summary_report(df):
    """Generate summary statistics"""
    print("\n" + "="*70)
    print("📊 WEKA-READY DATASET SUMMARY")
    print("="*70)
    
    print(f"\n📈 Dataset Dimensions:")
    print(f"   • Records: {len(df):,}")
    print(f"   • Features: {len(df.columns) - 1}")  # -1 for class label
    print(f"   • Class Label: Action_Taken")
    
    print(f"\n📋 Feature List:")
    for i, col in enumerate(df.columns, 1):
        dtype = 'Categorical' if df[col].dtype == 'object' else 'Numeric'
        print(f"   {i:2}. {col:<25} [{dtype}]")
    
    print(f"\n🎯 Class Distribution:")
    if 'Action_Taken' in df.columns:
        class_dist = df['Action_Taken'].value_counts()
        for class_name, count in class_dist.items():
            percentage = (count / len(df)) * 100
            print(f"   {class_name:<15} : {count:>6,} ({percentage:>5.2f}%)")
    
    print("\n" + "="*70)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main preprocessing pipeline"""
    
    print("\n" + "="*70)
    print("🚀 CSV TO WEKA PREPROCESSING PIPELINE")
    print("="*70 + "\n")
    
    try:
        # Step 1: Load CSV
        df = load_csv_completely(INPUT_CSV)
        
        # Step 2: Preprocess
        df_clean = clean_for_weka(df)
        
        # Step 3: Save
        save_weka_ready_csv(df_clean, OUTPUT_CSV)
        
        # Step 4: Summary
        generate_summary_report(df_clean)
        
        print("\n" + "="*70)
        print("🎉 PREPROCESSING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n✅ WEKA-ready file: {OUTPUT_CSV}")
        print(f"\n📝 Next Steps:")
        print(f"   1. Open WEKA Explorer")
        print(f"   2. Click 'Open file...'")
        print(f"   3. Select: weka_ready_dataset.csv")
        print(f"   4. Verify class attribute is 'Action_Taken'")
        print(f"   5. Proceed to classification modeling")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

# ============================================================================
# RUN PREPROCESSING
# ============================================================================

if __name__ == "__main__":
    main()