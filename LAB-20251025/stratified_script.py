import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("intrusion_det_log.csv")
target = "attack_type"
N = 5000

if target in df.columns and len(df) > N:
    stratified_sample, _ = train_test_split(
        df, train_size=N, stratify=df[target], random_state=42
    )
else:
    stratified_sample = df.copy()

stratified_sample.to_csv("intrusion_det_log_stratified_5000.csv", index=False)
print("Saved:", "intrusion_det_log_stratified_5000.csv")
print("Class proportions:\n", stratified_sample[target].value_counts(normalize=True))
