import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

def load_and_explore_data(file_path):
  print("=" * 50)
  print("LOADING AND EXPLORING DATASET")
  print("=" * 50)
  
  df = pd.read_csv(file_path)
  
  print(f"Dataset shape: {df.shape}")
  print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
  
  print("\nMissing Values:")
  missing_data = df.isnull().sum()
  missing_percent = (missing_data / len(df)) * 100
  missing_df = pd.DataFrame({
    'Missing Count': missing_data,
    'Missing Percentage': missing_percent
  })
  print(missing_df[missing_df['Missing Count'] > 0])
  
  print("\nData Types:")
  print(df.dtypes.value_counts())
  
  return df

def data_sanitation(df):
  print("\n" + "=" * 50)
  print("DATA SANITATION")
  print("=" * 50)
  
  df_clean = df.copy()
  
  print("\n1. HANDLING MISSING VALUES")
  print("-" * 25)
  
  categorical_cols = df_clean.select_dtypes(include=['object']).columns
  for col in categorical_cols:
    if df_clean[col].isnull().sum() > 0:
      mode_value = df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'Unknown'
      df_clean[col].fillna(mode_value, inplace=True)
      print(f"Filled '{col}' missing values with: {mode_value}")
  
  numerical_cols = df_clean.select_dtypes(include=['int64', 'float64']).columns
  for col in numerical_cols:
    if df_clean[col].isnull().sum() > 0:
      median_value = df_clean[col].median()
      df_clean[col].fillna(median_value, inplace=True)
      print(f"Filled '{col}' missing values with median: {median_value:.2f}")
  
  print("\n2. HANDLING DUPLICATES")
  print("-" * 25)
  
  initial_rows = len(df_clean)
  duplicates = df_clean.duplicated().sum()
  print(f"Found {duplicates} duplicate rows")
  
  if duplicates > 0:
    df_clean.drop_duplicates(inplace=True)
    print(f"Removed {duplicates} duplicate rows")
  
  print("\n3. HANDLING OUTLIERS")
  print("-" * 25)
  
  numerical_cols_for_outliers = ['Source Port', 'Destination Port', 'Packet Length', 'Anomaly Scores']
  
  for col in numerical_cols_for_outliers:
    if col in df_clean.columns:
      Q1 = df_clean[col].quantile(0.25)
      Q3 = df_clean[col].quantile(0.75)
      IQR = Q3 - Q1
      lower_bound = Q1 - 1.5 * IQR
      upper_bound = Q3 + 1.5 * IQR
      
      outliers = ((df_clean[col] < lower_bound) | 
           (df_clean[col] > upper_bound)).sum()
      
      print(f"Outliers in '{col}': {outliers} ({outliers/len(df_clean)*100:.2f}%)")
      
      df_clean[col] = np.where(df_clean[col] < lower_bound, lower_bound, df_clean[col])
      df_clean[col] = np.where(df_clean[col] > upper_bound, upper_bound, df_clean[col])
  
  print(f"\nData sanitation completed. Shape: {df_clean.shape}")
  return df_clean

def feature_extraction(df):
  print("\n" + "=" * 50)
  print("FEATURE EXTRACTION")
  print("=" * 50)
  
  df_features = df.copy()
  
  print("\n1. TEMPORAL FEATURE EXTRACTION")
  print("-" * 25)
  
  if 'Timestamp' in df_features.columns:
    df_features['Timestamp'] = pd.to_datetime(df_features['Timestamp'])
    df_features['Hour'] = df_features['Timestamp'].dt.hour
    df_features['DayOfWeek'] = df_features['Timestamp'].dt.dayofweek
    df_features['Month'] = df_features['Timestamp'].dt.month
    
    df_features['TimeOfDay'] = pd.cut(df_features['Hour'], 
                    bins=[0, 6, 12, 18, 24], 
                    labels=['Night', 'Morning', 'Afternoon', 'Evening'])
    
    print("Extracted: Hour, DayOfWeek, Month, TimeOfDay")
  
  print("\n2. IP ADDRESS FEATURE EXTRACTION")
  print("-" * 25)
  
  if 'Source IP Address' in df_features.columns:
    df_features['Source_IP_Class'] = df_features['Source IP Address'].str.split('.').str[0]
    df_features['Dest_IP_Class'] = df_features['Destination IP Address'].str.split('.').str[0]
    
    df_features['Source_IP_Type'] = df_features['Source_IP_Class'].apply(
      lambda x: 'Private' if x in ['10', '172', '192'] else 'Public'
    )
    df_features['Dest_IP_Type'] = df_features['Dest_IP_Class'].apply(
      lambda x: 'Private' if x in ['10', '172', '192'] else 'Public'
    )
    
    print("Extracted: IP classes and types")
  
  print("\n3. PORT FEATURE EXTRACTION")
  print("-" * 25)
  
  if 'Source Port' in df_features.columns:
    def categorize_port(port):
      if port <= 1023:
        return 'Well-known'
      elif port <= 49151:
        return 'Registered'
      else:
        return 'Dynamic'
    
    df_features['Source_Port_Category'] = df_features['Source Port'].apply(categorize_port)
    df_features['Dest_Port_Category'] = df_features['Destination Port'].apply(categorize_port)
    
    print("Extracted: Port categories")
  
  print("\n4. PACKET LENGTH FEATURE EXTRACTION")
  print("-" * 25)
  
  if 'Packet Length' in df_features.columns:
    df_features['Packet_Size_Category'] = pd.cut(df_features['Packet Length'], 
                          bins=[0, 64, 512, 1500, float('inf')], 
                          labels=['Small', 'Medium', 'Large', 'Jumbo'])
    
    df_features['Packet_Length_Log'] = np.log1p(df_features['Packet Length'])
    
    print("Extracted: Packet size categories and log transformation")
  
  print("\n5. GEO-LOCATION FEATURE EXTRACTION")
  print("-" * 25)
  
  if 'Geo-location Data' in df_features.columns:
    df_features['City'] = df_features['Geo-location Data'].str.split(',').str[0].str.strip()
    df_features['State'] = df_features['Geo-location Data'].str.split(',').str[1].str.strip()
    
    print("Extracted: City and State")
  
  print(f"\nFeature extraction completed. Shape: {df_features.shape}")
  return df_features

def encode_categorical_features(df):
  print("\n" + "=" * 50)
  print("CATEGORICAL FEATURE ENCODING")
  print("=" * 50)
  
  df_encoded = df.copy()
  
  categorical_cols = df_encoded.select_dtypes(include=['object', 'category']).columns.tolist()
  
  print(f"Found {len(categorical_cols)} categorical columns to encode")
  
  ordinal_features = ['Severity Level', 'Packet_Size_Category', 'TimeOfDay']
  label_encoders = {}
  
  for col in ordinal_features:
    if col in categorical_cols:
      le = LabelEncoder()
      df_encoded[col + '_encoded'] = le.fit_transform(df_encoded[col])
      label_encoders[col] = le
      print(f"Label encoded '{col}'")
  
  nominal_features = [col for col in categorical_cols if col not in ordinal_features]
  
  for col in nominal_features:
    unique_count = df_encoded[col].nunique()
    if unique_count <= 15: 
      dummies = pd.get_dummies(df_encoded[col], prefix=col, drop_first=True)
      df_encoded = pd.concat([df_encoded, dummies], axis=1)
      print(f"One-hot encoded '{col}' ({unique_count} categories)")
    else:
      print(f"Skipped '{col}' due to too many categories ({unique_count})")
  
  df_encoded.drop(columns=categorical_cols, inplace=True)
  
  print(f"\nEncoding completed. Shape: {df_encoded.shape}")
  return df_encoded, label_encoders

def feature_selection(df, target_column='Attack Type'):
  print("\n" + "=" * 50)
  print("FEATURE SELECTION")
  print("=" * 50)
  
  df_selected = df.copy()
  
  if target_column in df_selected.columns:
    target_col = target_column + '_encoded' if target_column + '_encoded' in df_selected.columns else target_column
    if target_col not in df_selected.columns:
      le = LabelEncoder()
      df_selected[target_col] = le.fit_transform(df_selected[target_column])
  else:
    target_col = 'Synthetic_Target'
    df_selected[target_col] = (df_selected['Anomaly Scores'] > 
                df_selected['Anomaly Scores'].median()).astype(int)
  
  feature_cols = [col for col in df_selected.columns if col != target_col]
  
  datetime_cols = df_selected.select_dtypes(include=['datetime64']).columns
  feature_cols = [col for col in feature_cols if col not in datetime_cols]
  
  X = df_selected[feature_cols]
  y = df_selected[target_col]
  
  print(f"Features shape: {X.shape}")
  print(f"Target shape: {y.shape}")
  
  print("\n1. CORRELATION-BASED FEATURE SELECTION")
  print("-" * 25)
  
  corr_matrix = X.corr().abs()
  
  high_corr_pairs = []
  for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
      if corr_matrix.iloc[i, j] > 0.95:
        high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
  
  print(f"Found {len(high_corr_pairs)} highly correlated feature pairs (>0.95)")
  
  features_to_remove = set()
  for feat1, feat2 in high_corr_pairs:
    if feat1 not in features_to_remove:
      features_to_remove.add(feat2)
  
  X_corr_filtered = X.drop(columns=list(features_to_remove))
  print(f"Removed {len(features_to_remove)} highly correlated features")
  
  print("\n2. UNIVARIATE FEATURE SELECTION")
  print("-" * 25)
  
  k_best = min(30, X_corr_filtered.shape[1])
  selector_f = SelectKBest(score_func=f_classif, k=k_best)
  X_f_selected = selector_f.fit_transform(X_corr_filtered, y)
  
  selected_features_f = X_corr_filtered.columns[selector_f.get_support()].tolist()
  print(f"Selected {len(selected_features_f)} features using f-test")
  
  print("\n3. MUTUAL INFORMATION FEATURE SELECTION")
  print("-" * 25)
  
  selector_mi = SelectKBest(score_func=mutual_info_classif, k=k_best)
  X_mi_selected = selector_mi.fit_transform(X_corr_filtered, y)
  
  selected_features_mi = X_corr_filtered.columns[selector_mi.get_support()].tolist()
  print(f"Selected {len(selected_features_mi)} features using mutual information")
  
  print("\n4. RANDOM FOREST FEATURE IMPORTANCE")
  print("-" * 25)
  
  rf = RandomForestClassifier(n_estimators=100, random_state=42)
  rf.fit(X_corr_filtered, y)
  
  feature_importance = pd.DataFrame({
    'feature': X_corr_filtered.columns,
    'importance': rf.feature_importances_
  }).sort_values('importance', ascending=False)
  
  threshold = 0.01
  important_features = feature_importance[feature_importance['importance'] > threshold]['feature'].tolist()
  
  print(f"Selected {len(important_features)} features using Random Forest importance")
  print("Top 10 most important features:")
  print(feature_importance.head(10))
  
  all_selected_features = list(set(selected_features_f + selected_features_mi + important_features))
  print(f"\nTotal unique selected features: {len(all_selected_features)}")
  
  X_final = X[all_selected_features]
  
  print(f"Final feature set shape: {X_final.shape}")
  
  return X_final, y, all_selected_features, feature_importance

def scale_features(X):
  print("\n" + "=" * 50)
  print("FEATURE SCALING")
  print("=" * 50)
  
  scaler = StandardScaler()
  X_scaled = scaler.fit_transform(X)
  
  print(f"Scaled features shape: {X_scaled.shape}")
  print("Applied StandardScaler (mean=0, std=1)")
  
  return X_scaled, scaler

def dimensionality_reduction(X_scaled):
  print("\n" + "=" * 50)
  print("DIMENSIONALITY REDUCTION")
  print("=" * 50)
  
  print("\n1. PRINCIPAL COMPONENT ANALYSIS (PCA)")
  print("-" * 25)
  
  pca_full = PCA()
  pca_full.fit(X_scaled)
  
  cumsum = np.cumsum(pca_full.explained_variance_ratio_)
  n_components_95 = np.argmax(cumsum >= 0.95) + 1
  
  print(f"Number of components for 95% variance: {n_components_95}")
  
  pca = PCA(n_components=n_components_95)
  X_pca = pca.fit_transform(X_scaled)
  
  print(f"PCA reduced features from {X_scaled.shape[1]} to {X_pca.shape[1]}")
  print(f"Explained variance ratio: {pca.explained_variance_ratio_.sum():.3f}")
  
  return X_pca, pca

def create_visualizations(X_scaled, X_pca, feature_importance, selected_features):
  print("\n" + "=" * 50)
  print("CREATING VISUALIZATIONS")
  print("=" * 50)
  
  plt.style.use('default')
  fig, axes = plt.subplots(2, 2, figsize=(15, 10))
  
  ax1 = axes[0, 0]
  corr_matrix = pd.DataFrame(X_scaled).corr()
  sns.heatmap(corr_matrix.iloc[:15, :15], annot=False, cmap='coolwarm', ax=ax1)
  ax1.set_title('Feature Correlation Heatmap (First 15 Features)')
  
  ax2 = axes[0, 1]
  pca_full = PCA()
  pca_full.fit(X_scaled)
  cumsum = np.cumsum(pca_full.explained_variance_ratio_)
  ax2.plot(range(1, len(cumsum) + 1), cumsum, 'b-', marker='o')
  ax2.axhline(y=0.95, color='r', linestyle='--', label='95% Variance')
  ax2.set_xlabel('Number of Components')
  ax2.set_ylabel('Cumulative Explained Variance')
  ax2.set_title('PCA Explained Variance')
  ax2.legend()
  ax2.grid(True)
  
  ax3 = axes[1, 0]
  if feature_importance is not None:
    feature_importance.head(10).plot(kind='bar', x='feature', y='importance', ax=ax3)
    ax3.set_title('Top 10 Most Important Features')
    ax3.set_xlabel('Features')
    ax3.set_ylabel('Importance')
    ax3.tick_params(axis='x', rotation=45)
  
  ax4 = axes[1, 1]
  if selected_features:
    feature_counts = pd.Series(selected_features).value_counts()
    feature_counts.head(10).plot(kind='bar', ax=ax4)
    ax4.set_title('Selected Features Distribution')
    ax4.set_xlabel('Features')
    ax4.set_ylabel('Count')
    ax4.tick_params(axis='x', rotation=45)
  
  plt.tight_layout()
  plt.savefig('cybersecurity_preprocessing_results.png', dpi=300, bbox_inches='tight')
  plt.show()
  
  print("Visualizations saved as 'cybersecurity_preprocessing_results.png'")

def main():
  print("CYBERSECURITY DATA PREPROCESSING PIPELINE")
  print("=" * 60)
  
  df = load_and_explore_data('20251025 - dataset - Wk12.csv')
  
  df_clean = data_sanitation(df)
  
  df_features = feature_extraction(df_clean)
  
  df_encoded, label_encoders = encode_categorical_features(df_features)
  
  X_selected, y, selected_features, feature_importance = feature_selection(df_encoded)
  
  X_scaled, scaler = scale_features(X_selected)
  
  X_pca, pca = dimensionality_reduction(X_scaled)
  
  create_visualizations(X_scaled, X_pca, feature_importance, selected_features)
  
  print("\n" + "=" * 50)
  print("SAVING RESULTS")
  print("=" * 50)
  
  df_encoded.to_csv('processed_cybersecurity_data.csv', index=False)
  print("Processed data saved as 'processed_cybersecurity_data.csv'")
  
  if selected_features:
    feature_df = pd.DataFrame({'feature_names': selected_features})
    feature_df.to_csv('selected_features.csv', index=False)
    print("Selected features saved as 'selected_features.csv'")
  
  if feature_importance is not None:
    feature_importance.to_csv('feature_importance.csv', index=False)
    print("Feature importance saved as 'feature_importance.csv'")
  
  print("\n" + "=" * 50)
  print("PREPROCESSING SUMMARY")
  print("=" * 50)
  
  print(f"Original dataset shape: {df.shape}")
  print(f"Processed dataset shape: {df_encoded.shape}")
  print(f"Selected features: {len(selected_features)}")
  print(f"Scaled features shape: {X_scaled.shape}")
  print(f"PCA features shape: {X_pca.shape}")
  print(f"Explained variance (PCA): {pca.explained_variance_ratio_.sum():.3f}")
  
  print("\nPreprocessing pipeline completed successfully!")
  
  return {
    'processed_data': df_encoded,
    'selected_features': X_selected,
    'scaled_features': X_scaled,
    'pca_features': X_pca,
    'target': y,
    'feature_names': selected_features,
    'scaler': scaler,
    'pca': pca,
    'label_encoders': label_encoders
  }

if __name__ == "__main__":
  try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn import datasets
  except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install required packages:")
    print("pip install pandas numpy matplotlib seaborn scikit-learn")
    exit(1)
  
  results = main()