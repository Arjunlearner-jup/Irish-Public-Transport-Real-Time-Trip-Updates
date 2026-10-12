import pandas as pd
import numpy as np
from pathlib import Path

input_file = Path("data") / "ireland_realtime_csv" / "trip_updates.csv"
output_file = Path("data_clean") / "final_clean.csv"

df = pd.read_csv(input_file, dtype={"trip_id": "string", "stop_id": "string"})

columns_to_delete = [
    "arrival_time",
    "arrival_uncertainty",
    "departure_time",
    "departure_uncertainty",
    "schedule_relationship",
    "trip_schedule_relationship",
]
df = df.drop(columns=columns_to_delete, errors="ignore")

# Remove rows where trip_id or stop_id is missing or blank
for col in ["trip_id", "stop_id"]:
    if col not in df.columns:
        raise KeyError(f"Required column not found: {col}")
    df[col] = df[col].str.strip()
    df = df.dropna(subset=[col])
    df = df[df[col].ne("")]

# Fill missing numeric values with the lower IQR bound
numeric_columns = df.select_dtypes(include=[np.number]).columns
for col in numeric_columns:
    if df[col].isna().any():
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        df[col] = df[col].fillna(q1 - 1.5 * iqr)

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print(f"Saved {len(df)} rows to {output_file}")