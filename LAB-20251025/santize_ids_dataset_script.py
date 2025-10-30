import pandas as pd

# === Load dataset ===
df = pd.read_csv("20251025 - dataset - Wk12.csv")

# === Fill missing values ===
fill_map = {
    "Malware Indicators": "No IoC Detected",
    "Alerts/Warnings": "No Alert Triggered",
    "Proxy Information": '?',
    "Firewall Logs": "No Log Data",
    "IDS/IPS Alerts": "No Alert Data"
}

for col, value in fill_map.items():
    if col in df.columns:
        df[col] = df[col].fillna(value)

# === Drop non-informative attribute ===
if "Payload Data" in df.columns:
    df = df.drop(columns=["Payload Data"])

# === Clean column names for MySQL ===
df.columns = (
    df.columns.str.strip()                # remove extra spaces
              .str.lower()                # make lowercase
              .str.replace(r"[^a-z0-9_]", "_", regex=True)  # replace invalid chars
              .str.replace(r"_+", "_", regex=True)           # collapse double underscores
              .str.strip("_")             # remove leading/trailing underscores
)

# === Sanitize text (replace newlines) ===
df = df.map(lambda x: str(x).replace("\n", " ") if isinstance(x, str) else x)

# === Save sanitized version ===
output_file = "intrusion_det_log.csv"
df.to_csv(output_file, index=False)
print(f"✅ Sanitized dataset saved as: {output_file}")
