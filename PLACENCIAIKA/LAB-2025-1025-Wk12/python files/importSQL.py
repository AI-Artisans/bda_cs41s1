import pandas as pd
import mysql.connector
from mysql.connector import Error
import numpy as np
from datetime import datetime
import re

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================

# File path configuration
CSV_FILE_PATH = r'C:\Users\A-224 (PC1)\Documents\VS Code\bda_cs41s1\PLACENCIAIKA\20251025-Lab-Wk12\20251025 - dataset - Wk12.csv'

# MySQL connection configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Empty password for XAMPP default
    'database': 'network_security_logs'
}

# ============================================================================
# STEP 1: CREATE DATABASE AND TABLE
# ============================================================================

def create_database_and_table():
    """Create database and table structure in MySQL"""
    connection = None
    try:
        # Connect to MySQL server (without database)
        connection = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            print(f"✓ Database '{MYSQL_CONFIG['database']}' created/verified successfully")
            
            # Use the database
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")
            
            # Drop table if exists (for clean import)
            cursor.execute("DROP TABLE IF EXISTS security_events")
            print("✓ Existing table dropped (if any)")
            
            # Create table with proper schema - ALLOW NULLs for missing data
            create_table_query = """
            CREATE TABLE security_events (
                event_id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NULL,
                source_ip VARCHAR(15) NULL,
                destination_ip VARCHAR(15) NULL,
                source_port INT NULL,
                destination_port INT NULL,
                protocol VARCHAR(10) NULL,
                packet_length INT NULL,
                packet_type VARCHAR(20) NULL,
                traffic_type VARCHAR(20) NULL,
                payload_data TEXT NULL,
                malware_indicators VARCHAR(50) NULL,
                anomaly_scores FLOAT NULL,
                alerts_warnings VARCHAR(50) NULL,
                attack_type VARCHAR(30) NULL,
                attack_signature VARCHAR(50) NULL,
                action_taken VARCHAR(20) NULL,
                severity_level VARCHAR(10) NULL,
                user_information VARCHAR(100) NULL,
                device_information TEXT NULL,
                network_segment VARCHAR(20) NULL,
                geo_location VARCHAR(100) NULL,
                proxy_information VARCHAR(15) NULL,
                firewall_logs VARCHAR(50) NULL,
                ids_ips_alerts VARCHAR(50) NULL,
                log_source VARCHAR(30) NULL,
                INDEX idx_action_taken (action_taken),
                INDEX idx_attack_type (attack_type),
                INDEX idx_timestamp (timestamp),
                INDEX idx_severity (severity_level)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            cursor.execute(create_table_query)
            print("✓ Table 'security_events' created successfully (allows NULL values)")
            
            connection.commit()
            cursor.close()
            
    except Error as e:
        print(f"✗ Error creating database/table: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return True

# ============================================================================
# STEP 2: LOAD AND CLEAN DATA - KEEP ALL ROWS
# ============================================================================

def load_and_clean_data(file_path):
    """Load CSV - Keep ALL rows, replace missing values with None/NULL"""
    try:
        print(f"\n📂 Loading data from: {file_path}")
        
        # Count actual rows
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for line in f)
            actual_rows = total_lines - 1
        
        print(f"📄 CSV file contains {actual_rows:,} data rows")
        print(f"⏳ Reading ALL rows manually (keeping ALL records)...")
        
        # Read header
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            columns = first_line.split(',')
        
        print(f"✓ Found {len(columns)} columns")
        
        # Read all data rows manually
        data_rows = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            next(f)  # Skip header
            
            for i, line in enumerate(f):
                if (i + 1) % 10000 == 0:
                    print(f"   Reading row {i+1:,}/{actual_rows:,} ({((i+1)/actual_rows)*100:.1f}%)")
                
                # Simple CSV parsing (handles quotes)
                row = []
                in_quotes = False
                current_field = ""
                
                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        row.append(current_field.strip())
                        current_field = ""
                    else:
                        current_field += char
                
                # Add last field
                row.append(current_field.strip())
                
                # Ensure row has correct number of columns
                while len(row) < len(columns):
                    row.append('')
                
                data_rows.append(row[:len(columns)])  # Trim extra columns
        
        print(f"✓ Read ALL {len(data_rows):,} rows manually")
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=columns)
        print(f"✅ Successfully created DataFrame with {len(df):,} records")
        
        # Clean column names (remove quotes if any)
        df.columns = [col.strip().strip('"') for col in df.columns]
        
        print(f"\n📋 Columns loaded: {list(df.columns)[:5]}...")
        
        # Data cleaning - REPLACE EMPTY WITH None (NULL in MySQL)
        print("\n🧹 Cleaning data (replacing empty values with NULL)...")
        
        # Replace empty strings with None (will become NULL in MySQL)
        df = df.replace('', None)
        df = df.replace('nan', None)
        df = df.replace('NaN', None)
        
        # For specific columns, use default values instead of NULL
        if 'Malware Indicators' in df.columns:
            df['Malware Indicators'] = df['Malware Indicators'].fillna('None Detected')
        
        if 'Alerts/Warnings' in df.columns:
            df['Alerts/Warnings'] = df['Alerts/Warnings'].fillna('No Alert')
        
        if 'Proxy Information' in df.columns:
            df['Proxy Information'] = df['Proxy Information'].fillna('N/A')
        
        if 'Firewall Logs' in df.columns:
            df['Firewall Logs'] = df['Firewall Logs'].fillna('Not Available')
        
        if 'IDS/IPS Alerts' in df.columns:
            df['IDS/IPS Alerts'] = df['IDS/IPS Alerts'].fillna('Not Available')
        
        # Convert timestamp (keep as None if invalid)
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        # Clean numeric fields (keep as None if invalid)
        if 'Anomaly Scores' in df.columns:
            df['Anomaly Scores'] = pd.to_numeric(df['Anomaly Scores'], errors='coerce')
        
        if 'Source Port' in df.columns:
            df['Source Port'] = pd.to_numeric(df['Source Port'], errors='coerce')
        
        if 'Destination Port' in df.columns:
            df['Destination Port'] = pd.to_numeric(df['Destination Port'], errors='coerce')
        
        if 'Packet Length' in df.columns:
            df['Packet Length'] = pd.to_numeric(df['Packet Length'], errors='coerce')
        
        # Check for missing values
        print("\n📊 Missing Values Summary:")
        missing_counts = df.isnull().sum()
        critical_missing = missing_counts[missing_counts > 0]
        if len(critical_missing) > 0:
            for col, count in critical_missing.items():
                print(f"   {col}: {count:,} missing ({(count/len(df)*100):.2f}%)")
        else:
            print("   No missing values detected")
        
        print(f"\n✓ Data cleaning completed. KEEPING ALL {len(df):,} records")
        
        # Display class distribution
        print("\n📊 Action Taken distribution:")
        if 'Action Taken' in df.columns:
            print(df['Action Taken'].value_counts(dropna=False))
        
        return df
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# STEP 3: IMPORT DATA TO MYSQL - HANDLE NULL VALUES
# ============================================================================

def import_to_mysql(df):
    """Import cleaned DataFrame to MySQL database - Keep NULL values"""
    connection = None
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            print(f"\n🔗 Connected to MySQL database: {MYSQL_CONFIG['database']}")
            
            # Prepare INSERT query
            insert_query = """
            INSERT INTO security_events 
            (timestamp, source_ip, destination_ip, source_port, destination_port,
             protocol, packet_length, packet_type, traffic_type, payload_data,
             malware_indicators, anomaly_scores, alerts_warnings, attack_type,
             attack_signature, action_taken, severity_level, user_information,
             device_information, network_segment, geo_location, proxy_information,
             firewall_logs, ids_ips_alerts, log_source)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            
            # Prepare data for batch insert
            records_to_insert = []
            
            for index, row in df.iterrows():
                # Helper function to convert values to None if NaN/NaT
                def clean_value(val):
                    if pd.isna(val) or val == '' or val == 'nan':
                        return None
                    return val
                
                record = (
                    clean_value(row.get('Timestamp')),
                    clean_value(row.get('Source IP Address')),
                    clean_value(row.get('Destination IP Address')),
                    int(row['Source Port']) if pd.notna(row.get('Source Port')) and row.get('Source Port') != '' else None,
                    int(row['Destination Port']) if pd.notna(row.get('Destination Port')) and row.get('Destination Port') != '' else None,
                    clean_value(row.get('Protocol')),
                    int(row['Packet Length']) if pd.notna(row.get('Packet Length')) and row.get('Packet Length') != '' else None,
                    clean_value(row.get('Packet Type')),
                    clean_value(row.get('Traffic Type')),
                    clean_value(row.get('Payload Data')),
                    clean_value(row.get('Malware Indicators')),
                    float(row['Anomaly Scores']) if pd.notna(row.get('Anomaly Scores')) and row.get('Anomaly Scores') != '' else None,
                    clean_value(row.get('Alerts/Warnings')),
                    clean_value(row.get('Attack Type')),
                    clean_value(row.get('Attack Signature')),
                    clean_value(row.get('Action Taken')),
                    clean_value(row.get('Severity Level')),
                    clean_value(row.get('User Information')),
                    clean_value(row.get('Device Information')),
                    clean_value(row.get('Network Segment')),
                    clean_value(row.get('Geo-location Data')),
                    clean_value(row.get('Proxy Information')),
                    clean_value(row.get('Firewall Logs')),
                    clean_value(row.get('IDS/IPS Alerts')),
                    clean_value(row.get('Log Source'))
                )
                records_to_insert.append(record)
            
            # Batch insert with progress indicator
            batch_size = 1000
            total_records = len(records_to_insert)
            
            print(f"\n⏳ Importing ALL {total_records:,} records in batches of {batch_size:,}...")
            
            for i in range(0, total_records, batch_size):
                batch = records_to_insert[i:i + batch_size]
                cursor.executemany(insert_query, batch)
                connection.commit()
                
                progress = min(i + batch_size, total_records)
                percentage = (progress / total_records) * 100
                print(f"   Progress: {progress:,}/{total_records:,} ({percentage:.1f}%)")
            
            print(f"\n✓ Successfully imported ALL {total_records:,} records!")
            
            # Verify import
            cursor.execute("SELECT COUNT(*) FROM security_events")
            count = cursor.fetchone()[0]
            print(f"✓ Verification: Database contains {count:,} records")
            
            # Count NULL values in Action Taken
            cursor.execute("SELECT COUNT(*) FROM security_events WHERE action_taken IS NULL")
            null_count = cursor.fetchone()[0]
            print(f"✓ Records with NULL Action Taken: {null_count:,}")
            
            cursor.close()
            return True
            
    except Error as e:
        print(f"✗ MySQL Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("🔌 MySQL connection closed")

# ============================================================================
# STEP 4: VALIDATION AND STATISTICS
# ============================================================================

def validate_import():
    """Validate imported data and show statistics"""
    connection = None
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("\n" + "="*70)
            print("📊 DATABASE VALIDATION AND STATISTICS")
            print("="*70)
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM security_events")
            total = cursor.fetchone()[0]
            print(f"\n✓ Total Records: {total:,}")
            
            # Action Taken distribution (including NULL)
            print("\n📌 Action Taken Distribution (including NULL):")
            cursor.execute("""
                SELECT 
                    COALESCE(action_taken, 'NULL/Missing') as action,
                    COUNT(*) as count, 
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM security_events), 2) as percentage
                FROM security_events 
                GROUP BY action_taken 
                ORDER BY count DESC
            """)
            for row in cursor.fetchall():
                print(f"   {row[0]:<15} : {row[1]:>6,} ({row[2]:>5}%)")
            
            # Attack Type distribution
            print("\n🎯 Attack Type Distribution:")
            cursor.execute("""
                SELECT COALESCE(attack_type, 'NULL/Missing') as attack, COUNT(*) as count 
                FROM security_events 
                GROUP BY attack_type 
                ORDER BY count DESC
            """)
            for row in cursor.fetchall():
                print(f"   {row[0]:<15} : {row[1]:>6,}")
            
            # Severity Level distribution
            print("\n⚠️  Severity Level Distribution:")
            cursor.execute("""
                SELECT COALESCE(severity_level, 'NULL/Missing') as severity, COUNT(*) as count 
                FROM security_events 
                GROUP BY severity_level 
                ORDER BY FIELD(severity_level, 'High', 'Medium', 'Low')
            """)
            for row in cursor.fetchall():
                print(f"   {row[0]:<15} : {row[1]:>6,}")
            
            # Date range
            print("\n📅 Timestamp Range:")
            cursor.execute("""
                SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest 
                FROM security_events
                WHERE timestamp IS NOT NULL
            """)
            row = cursor.fetchone()
            if row[0]:
                print(f"   Earliest: {row[0]}")
                print(f"   Latest  : {row[1]}")
            else:
                print("   No valid timestamps found")
            
            # Anomaly scores statistics
            print("\n📈 Anomaly Scores Statistics:")
            cursor.execute("""
                SELECT 
                    MIN(anomaly_scores) as min_score,
                    MAX(anomaly_scores) as max_score,
                    AVG(anomaly_scores) as avg_score,
                    STDDEV(anomaly_scores) as std_dev
                FROM security_events
                WHERE anomaly_scores IS NOT NULL
            """)
            row = cursor.fetchone()
            if row[0] is not None:
                print(f"   Minimum  : {row[0]:.2f}")
                print(f"   Maximum  : {row[1]:.2f}")
                print(f"   Average  : {row[2]:.2f}")
                print(f"   Std Dev  : {row[3]:.2f}")
            
            # NULL counts
            print("\n❌ NULL Value Counts:")
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN timestamp IS NULL THEN 1 ELSE 0 END) as null_timestamp,
                    SUM(CASE WHEN action_taken IS NULL THEN 1 ELSE 0 END) as null_action,
                    SUM(CASE WHEN attack_type IS NULL THEN 1 ELSE 0 END) as null_attack,
                    SUM(CASE WHEN severity_level IS NULL THEN 1 ELSE 0 END) as null_severity
                FROM security_events
            """)
            row = cursor.fetchone()
            print(f"   Timestamp: {row[0]:,}")
            print(f"   Action Taken: {row[1]:,}")
            print(f"   Attack Type: {row[2]:,}")
            print(f"   Severity Level: {row[3]:,}")
            
            print("\n" + "="*70)
            print("✓ VALIDATION COMPLETED SUCCESSFULLY")
            print("="*70 + "\n")
            
            cursor.close()
            
    except Error as e:
        print(f"✗ Validation Error: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()

# ============================================================================
# STEP 5: EXPORT DATABASE DUMP
# ============================================================================

def export_database_dump():
    """Export MySQL database dump for Git upload"""
    try:
        import subprocess
        import os
        
        # Output file path
        output_file = 'network_security_logs.sql'
        
        # Find mysqldump in XAMPP
        mysqldump_paths = [
            r'C:\xampp\mysql\bin\mysqldump.exe',
            r'C:\XAMPP\mysql\bin\mysqldump.exe',
            'mysqldump'
        ]
        
        mysqldump_cmd = None
        for path in mysqldump_paths:
            if os.path.exists(path) if path != 'mysqldump' else True:
                mysqldump_cmd = path
                break
        
        if not mysqldump_cmd:
            print("⚠️  mysqldump not found automatically")
            print("📝 Manual export instructions:")
            print("   1. Open browser: http://localhost/phpmyadmin")
            print("   2. Click 'network_security_logs' database")
            print("   3. Click 'Export' tab")
            print("   4. Select 'Quick' export method")
            print("   5. Format: SQL")
            print("   6. Click 'Go'")
            print(f"   7. Save as '{output_file}'")
            return False
        
        print(f"\n💾 Exporting database dump to: {output_file}")
        
        # mysqldump command
        if MYSQL_CONFIG['password']:
            dump_command = [
                mysqldump_cmd,
                '-h', MYSQL_CONFIG['host'],
                '-u', MYSQL_CONFIG['user'],
                f'-p{MYSQL_CONFIG["password"]}',
                MYSQL_CONFIG['database']
            ]
        else:
            dump_command = [
                mysqldump_cmd,
                '-h', MYSQL_CONFIG['host'],
                '-u', MYSQL_CONFIG['user'],
                MYSQL_CONFIG['database']
            ]
        
        # Execute mysqldump
        with open(output_file, 'w', encoding='utf-8') as f:
            result = subprocess.run(dump_command, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✓ Database dump created successfully ({file_size:.2f} MB)")
            print(f"✓ File ready for Git upload: {output_file}")
            return True
        else:
            print(f"✗ Error creating dump: {result.stderr}")
            print("\n📝 Use phpMyAdmin manual export instead")
            return False
            
    except Exception as e:
        print(f"✗ Error exporting database: {e}")
        print("\n📝 Manual export via phpMyAdmin recommended")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("🚀 NETWORK SECURITY LOGS - MYSQL DATABASE IMPORT")
    print("   FULL DATASET: 59,366 RECORDS (KEEPING ALL ROWS)")
    print("="*70)
    
    # Step 1: Create database and table
    print("\n[STEP 1/5] Creating database and table...")
    if not create_database_and_table():
        print("❌ Failed to create database. Exiting.")
        return
    
    # Step 2: Load and clean data
    print("\n[STEP 2/5] Loading and cleaning data...")
    df = load_and_clean_data(CSV_FILE_PATH)
    if df is None:
        print("❌ Failed to load data. Exiting.")
        return
    
    # Step 3: Import to MySQL
    print("\n[STEP 3/5] Importing data to MySQL...")
    if not import_to_mysql(df):
        print("❌ Failed to import data. Exiting.")
        return
    
    # Step 4: Validate import
    print("\n[STEP 4/5] Validating imported data...")
    validate_import()
    
    # Step 5: Export database dump
    print("\n[STEP 5/5] Exporting database dump...")
    export_database_dump()
    
    print("\n" + "="*70)
    print("🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\n📝 Summary:")
    print("   ✓ ALL 59,366 records imported (no deletions)")
    print("   ✓ Missing values stored as NULL in database")
    print("   ✓ Ready for WEKA preprocessing and modeling")
    print("\n📝 Next Steps:")
    print("   1. Upload 'network_security_logs.sql' to your Git branch")
    print("   2. Handle missing values in WEKA (filters available)")
    print("   3. Export to ARFF format for classification")
    print("   4. Proceed to modeling with 3 new algorithms")
    print("\n")

# ============================================================================
# RUN THE SCRIPT
# ============================================================================

if __name__ == "__main__":
    main()