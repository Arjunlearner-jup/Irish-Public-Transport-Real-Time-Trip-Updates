import pandas as pd
from pathlib import Path

table1_file = Path("data_clean") / "trip_updates_one_row_per_trip.csv"
table2_file = Path("data_clean") / "static_realtime_merged.csv"

# Check that both files exist
for file_path in [table1_file, table2_file]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path.resolve()}")

# Load the CSVs
table1 = pd.read_csv(table1_file)
table2 = pd.read_csv(table2_file)

# Count rows
table1_count = len(table1)
table2_count = len(table2)

print(f"Rows in table1: {table1_count}")
print(f"Rows in table2: {table2_count}")

if table1_count == 0:
    print("Cannot calculate result: table1 has 0 rows.")
else:
    result = (table2_count / table1_count) * 100
    print(f"Result: {result:.2f}%")