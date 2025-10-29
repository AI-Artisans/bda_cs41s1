import pandas as pd
import numpy as np
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, cohen_kappa_score, 
                             precision_recall_fscore_support, confusion_matrix)
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import warnings
import os
import pickle
import json
from datetime import datetime
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

ARFF_FILE = "weka_ready_dataset.arff"
OUTPUT_DIR = "models"  # Directory to save models
RESULTS_FILE = "model_comparison_results.csv"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_arff(file_path):
    """Load ARFF file and convert to pandas DataFrame"""
    print(f"Loading file: {file_path}")
    data, meta = arff.loadarff(file_path)
    df = pd.DataFrame(data)
    
    # Convert byte strings to regular strings
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = df[col].str.decode('utf-8')
            except:
                pass
    
    return df

def evaluate_model(y_true, y_pred, model_name):
    """Calculate all required metrics"""
    # Convert labels if needed
    le = LabelEncoder()
    y_true_encoded = le.fit_transform(y_true)
    y_pred_encoded = le.transform(y_pred)
    
    # Total instances
    total = len(y_true)
    
    # Correctly and Incorrectly Classified
    correct = accuracy_score(y_true_encoded, y_pred_encoded, normalize=False)
    incorrect = total - correct
    
    # Accuracy
    accuracy = accuracy_score(y_true_encoded, y_pred_encoded)
    
    # Kappa Statistics
    kappa = cohen_kappa_score(y_true_encoded, y_pred_encoded)
    
    # Precision, Recall, F-Measure for each class
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true_encoded, y_pred_encoded, average=None, zero_division=0
    )
    
    # Weighted average F1 score (for overall model comparison)
    weighted_f1 = np.average(f1, weights=support)
    
    # Confusion Matrix
    cm = confusion_matrix(y_true_encoded, y_pred_encoded)
    
    # Get class names
    classes = le.classes_
    
    results = {
        'Model': model_name,
        'Total Instances': total,
        'Correctly Classified': correct,
        'Incorrectly Classified': incorrect,
        'Accuracy': accuracy,
        'Accuracy_Display': f"{accuracy:.4f} ({accuracy*100:.2f}%)",
        'Kappa Statistic': kappa,
        'Kappa_Display': f"{kappa:.4f}",
        'Weighted_F1': weighted_f1,  # For determining best model
    }
    
    # Add metrics for each class
    for i, cls in enumerate(classes):
        results[f'Precision (Class: {cls})'] = precision[i]
        results[f'Recall (Class: {cls})'] = recall[i]
        results[f'F-Measure (Class: {cls})'] = f1[i]
        results[f'Precision_Display (Class: {cls})'] = f"{precision[i]:.4f}"
        results[f'Recall_Display (Class: {cls})'] = f"{recall[i]:.4f}"
        results[f'F-Measure_Display (Class: {cls})'] = f"{f1[i]:.4f}"
    
    return results, cm, classes

def save_model(model, model_name, encoders, metadata, output_dir):
    """Save trained model with encoders and metadata"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create model filename
    model_filename = f"{model_name}_{timestamp}.model"
    model_path = os.path.join(output_dir, model_filename)
    
    # Save model based on type
    if isinstance(model, xgb.XGBClassifier):
        model.save_model(model_path)
    elif isinstance(model, lgb.LGBMClassifier):
        model.booster_.save_model(model_path)
    elif isinstance(model, cb.CatBoostClassifier):
        model.save_model(model_path)
    
    # Save encoders
    encoders_filename = f"{model_name}_{timestamp}_encoders.pkl"
    encoders_path = os.path.join(output_dir, encoders_filename)
    with open(encoders_path, 'wb') as f:
        pickle.dump(encoders, f)
    
    # Save metadata
    metadata_filename = f"{model_name}_{timestamp}_metadata.json"
    metadata_path = os.path.join(output_dir, metadata_filename)
    
    # Convert numpy types to native Python types for JSON serialization
    metadata_serializable = {}
    for key, value in metadata.items():
        if isinstance(value, (np.integer, np.floating)):
            metadata_serializable[key] = float(value)
        elif isinstance(value, np.ndarray):
            metadata_serializable[key] = value.tolist()
        else:
            metadata_serializable[key] = value
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata_serializable, f, indent=4)
    
    print(f"\n✓ Model saved:")
    print(f"   Model: {model_path}")
    print(f"   Encoders: {encoders_path}")
    print(f"   Metadata: {metadata_path}")
    
    return model_path, encoders_path, metadata_path

def determine_best_model(results_list):
    """Determine the best model based on accuracy and weighted F1 score"""
    
    best_model_idx = 0
    best_score = -1
    
    # Primary: Accuracy, Secondary: Weighted F1
    for i, result in enumerate(results_list):
        # Composite score: 70% accuracy + 30% weighted F1
        score = 0.7 * result['Accuracy'] + 0.3 * result['Weighted_F1']
        
        if score > best_score:
            best_score = score
            best_model_idx = i
    
    return best_model_idx, best_score

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main(arff_file_path):
    print("="*80)
    print("CLASSIFICATION MODEL COMPARISON: XGBoost vs LightGBM vs CatBoost")
    print("="*80)
    
    # Check if file exists
    if not os.path.exists(arff_file_path):
        print(f"❌ Error: File not found at '{arff_file_path}'")
        print(f"Current directory: {os.getcwd()}")
        return
    
    # Load data
    print(f"\n📂 Loading ARFF file...")
    df = load_arff(arff_file_path)
    print(f"✓ Data loaded successfully: {df.shape[0]} instances, {df.shape[1]} attributes")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Prepare data (assuming last column is the target)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    
    print(f"\n📊 Dataset Information:")
    print(f"   Features: {X.shape[1]}")
    print(f"   Target variable: {df.columns[-1]}")
    print(f"   Target classes: {y.unique()}")
    print(f"   Class distribution:\n{y.value_counts()}")
    
    # Encode categorical features
    le_features = {}
    for col in X.columns:
        if X[col].dtype == 'object':
            le_features[col] = LabelEncoder()
            X[col] = le_features[col].fit_transform(X[col])
    
    # Split data (70% train, 30% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"\n✓ Data split: {len(X_train)} training, {len(X_test)} testing instances")
    
    # Encode target variable for model training
    le_target = LabelEncoder()
    y_train_encoded = le_target.fit_transform(y_train)
    y_test_encoded = le_target.transform(y_test)
    
    # Store all encoders
    all_encoders = {
        'feature_encoders': le_features,
        'target_encoder': le_target
    }
    
    results_list = []
    trained_models = []
    model_names = []
    
    # ========================
    # 1. XGBoost
    # ========================
    print("\n" + "="*80)
    print("🚀 Training XGBoost...")
    print("="*80)
    
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False
    )
    xgb_model.fit(X_train, y_train_encoded)
    xgb_pred = xgb_model.predict(X_test)
    xgb_pred_labels = le_target.inverse_transform(xgb_pred)
    
    xgb_results, xgb_cm, classes = evaluate_model(y_test, xgb_pred_labels, 'XGBoost')
    results_list.append(xgb_results)
    trained_models.append(xgb_model)
    model_names.append('XGBoost')
    
    print("✓ XGBoost training complete")
    
    # ========================
    # 2. LightGBM
    # ========================
    print("\n" + "="*80)
    print("🚀 Training LightGBM...")
    print("="*80)
    
    lgb_model = lgb.LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        verbose=-1
    )
    lgb_model.fit(X_train, y_train_encoded)
    lgb_pred = lgb_model.predict(X_test)
    lgb_pred_labels = le_target.inverse_transform(lgb_pred)
    
    lgb_results, lgb_cm, _ = evaluate_model(y_test, lgb_pred_labels, 'LightGBM')
    results_list.append(lgb_results)
    trained_models.append(lgb_model)
    model_names.append('LightGBM')
    
    print("✓ LightGBM training complete")
    
    # ========================
    # 3. CatBoost
    # ========================
    print("\n" + "="*80)
    print("🚀 Training CatBoost...")
    print("="*80)
    
    cb_model = cb.CatBoostClassifier(
        iterations=100,
        depth=6,
        learning_rate=0.1,
        random_state=42,
        verbose=False
    )
    cb_model.fit(X_train, y_train_encoded)
    cb_pred = cb_model.predict(X_test)
    cb_pred_labels = le_target.inverse_transform(cb_pred.astype(int))
    
    cb_results, cb_cm, _ = evaluate_model(y_test, cb_pred_labels, 'CatBoost')
    results_list.append(cb_results)
    trained_models.append(cb_model)
    model_names.append('CatBoost')
    
    print("✓ CatBoost training complete")
    
    # ========================
    # Determine Best Model
    # ========================
    print("\n" + "="*80)
    print("🏆 DETERMINING BEST MODEL")
    print("="*80)
    
    best_idx, best_score = determine_best_model(results_list)
    best_model = trained_models[best_idx]
    best_model_name = model_names[best_idx]
    
    print(f"\n✓ Best Model: {best_model_name}")
    print(f"  Accuracy: {results_list[best_idx]['Accuracy']:.4f} ({results_list[best_idx]['Accuracy']*100:.2f}%)")
    print(f"  Weighted F1: {results_list[best_idx]['Weighted_F1']:.4f}")
    print(f"  Kappa: {results_list[best_idx]['Kappa Statistic']:.4f}")
    print(f"  Composite Score: {best_score:.4f}")
    
    # ========================
    # Save Best Model
    # ========================
    print("\n" + "="*80)
    print("💾 SAVING BEST MODEL")
    print("="*80)
    
    metadata = {
        'model_name': best_model_name,
        'accuracy': float(results_list[best_idx]['Accuracy']),
        'kappa': float(results_list[best_idx]['Kappa Statistic']),
        'weighted_f1': float(results_list[best_idx]['Weighted_F1']),
        'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_instances': int(results_list[best_idx]['Total Instances']),
        'correctly_classified': int(results_list[best_idx]['Correctly Classified']),
        'target_classes': le_target.classes_.tolist(),
        'feature_names': X.columns.tolist(),
        'test_size': 0.3,
        'random_state': 42
    }
    
    # Add per-class metrics
    for cls in classes:
        metadata[f'precision_{cls}'] = float(results_list[best_idx][f'Precision (Class: {cls})'])
        metadata[f'recall_{cls}'] = float(results_list[best_idx][f'Recall (Class: {cls})'])
        metadata[f'f1_{cls}'] = float(results_list[best_idx][f'F-Measure (Class: {cls})'])
    
    model_path, encoders_path, metadata_path = save_model(
        best_model, 
        best_model_name, 
        all_encoders, 
        metadata, 
        OUTPUT_DIR
    )
    
    # ========================
    # Display Results
    # ========================
    print("\n" + "="*80)
    print("📊 RESULTS SUMMARY")
    print("="*80)
    
    # Print detailed results for each model
    for model_results in results_list:
        print(f"\n{'='*60}")
        print(f"{model_results['Model']} RESULTS")
        print(f"{'='*60}")
        print(f"{'Total Instances':<40} {model_results['Total Instances']}")
        print(f"{'Correctly Classified':<40} {model_results['Correctly Classified']}")
        print(f"{'Incorrectly Classified':<40} {model_results['Incorrectly Classified']}")
        print(f"{'Accuracy':<40} {model_results['Accuracy_Display']}")
        print(f"{'Kappa Statistic':<40} {model_results['Kappa_Display']}")
        
        for cls in classes:
            print(f"{'Precision (Class: ' + cls + ')':<40} {model_results[f'Precision_Display (Class: {cls})']}")
            print(f"{'Recall (Class: ' + cls + ')':<40} {model_results[f'Recall_Display (Class: {cls})']}")
            print(f"{'F-Measure (Class: ' + cls + ')':<40} {model_results[f'F-Measure_Display (Class: {cls})']}")
    
    # Highlight best model
    print(f"\n{'='*60}")
    print(f"🏆 BEST MODEL: {best_model_name}")
    print(f"{'='*60}")
    
    # Create comparison table
    print("\n" + "="*80)
    print("📋 COMPARISON TABLE")
    print("="*80)
    
    metrics_list = [
        'Correctly Classified Instances',
        'Incorrectly Classified Instances',
        'Kappa Statistic',
    ]
    
    for cls in classes:
        metrics_list.extend([
            f'Precision (Class: {cls})',
            f'Recall (Class: {cls})',
            f'F-Measure (Class: {cls})'
        ])
    
    comparison_data = {'Metric': metrics_list}
    
    for i, model_name in enumerate(model_names):
        model_data = []
        model_data.append(results_list[i]['Correctly Classified'])
        model_data.append(results_list[i]['Incorrectly Classified'])
        model_data.append(results_list[i]['Kappa_Display'])
        
        for cls in classes:
            model_data.append(results_list[i][f'Precision_Display (Class: {cls})'])
            model_data.append(results_list[i][f'Recall_Display (Class: {cls})'])
            model_data.append(results_list[i][f'F-Measure_Display (Class: {cls})'])
        
        comparison_data[model_name] = model_data
    
    comparison_table = pd.DataFrame(comparison_data)
    
    print("\n" + comparison_table.to_string(index=False))
    
    # Save to CSV
    comparison_table.to_csv(RESULTS_FILE, index=False)
    print(f"\n✓ Results saved to '{RESULTS_FILE}'")
    
    # ========================
    # Final Summary
    # ========================
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\n📁 Output Files:")
    print(f"   • Best Model: {model_path}")
    print(f"   • Encoders: {encoders_path}")
    print(f"   • Metadata: {metadata_path}")
    print(f"   • Results: {RESULTS_FILE}")
    print(f"\n🏆 Best Performing Model: {best_model_name}")
    print(f"   Accuracy: {results_list[best_idx]['Accuracy']*100:.2f}%")
    print("\n")

# ============================================================================
# RUN THE ANALYSIS
# ============================================================================

if __name__ == "__main__":
    print(f"Looking for file: {ARFF_FILE}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}\n")
    
    try:
        main(ARFF_FILE)
    except FileNotFoundError:
        print(f"\n❌ Error: File not found!")
        print(f"\nTroubleshooting:")
        print(f"1. Make sure the file 'weka_ready_dataset.arff' exists")
        print(f"2. Run this script from the same directory as your .arff file")
        print(f"3. Or update ARFF_FILE variable with the correct path")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()