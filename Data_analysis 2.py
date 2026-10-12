import pandas as pd
from pathlib import Path

# Load tables

table1 = pd.read_csv(Path("data_clean") / "final_clean.csv", dtype=str)

table2 = pd.read_csv(Path("GTFS_Static")/ "stop_times.txt", dtype=str)

# Clean column names
table1.columns = table1.columns.str.strip().str.lower()
table2.columns = table2.columns.str.strip().str.lower()

# Clean trip_id
table1["trip_id"] = table1["trip_id"].astype(str).str.strip()
table2["trip_id"] = table2["trip_id"].astype(str).str.strip()

# Convert stop_sequence to integer
table1["stop_sequence"] = pd.to_numeric(
    table1["stop_sequence"], errors="coerce"
).astype("Int64")

table2["stop_sequence"] = pd.to_numeric(
    table2["stop_sequence"], errors="coerce"
).astype("Int64")

# Remove missing join keys
table1 = table1.dropna(subset=["trip_id", "stop_sequence"])
table2 = table2.dropna(subset=["trip_id", "stop_sequence"])

# Diagnostics
print("\n--- JOIN KEY DIAGNOSTICS ---")

print("\nfinal_clean sample:")
print(table1[["trip_id", "stop_sequence"]].head(10))

print("\nstop_times sample:")
print(table2[["trip_id", "stop_sequence"]].head(10))

common_trip_ids = set(table1["trip_id"]) & set(table2["trip_id"])
common_stop_sequences = set(table1["stop_sequence"]) & set(table2["stop_sequence"])

print(f"\nCommon trip_ids: {len(common_trip_ids)}")
print(f"Common stop_sequences: {len(common_stop_sequences)}")

print("\nSample real-time trip_id check:")
sample_trip_id = table1["trip_id"].iloc[0]
print(f"Trip ID: {sample_trip_id}")
print("Exists in stop_times:", sample_trip_id in set(table2["trip_id"]))

print(
    table2[table2["trip_id"] == sample_trip_id][
        ["trip_id", "stop_sequence", "stop_id"]
    ].head()
)

# Join where BOTH trip_id and stop_sequence match
merged = table1.merge(
    table2,
    on=["trip_id", "stop_sequence"],
    how="inner",
    suffixes=("_final_clean", "_stop_times")
)

# Save output
output_file = Path("Data analysis") / "final_clean_stop_times_joined.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
merged.to_csv(output_file, index=False)

print(f"\nRows in final_clean.csv: {len(table1)}")
print(f"Rows in stop_times.csv: {len(table2)}")
print(f"Rows in joined output: {len(merged)}")
print(merged.head())