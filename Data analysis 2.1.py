import pandas as pd
from pathlib import Path

table1 = pd.read_csv(Path("Data analysis") / "final_clean_stop_times_joined.csv", dtype=str)

# Show first rows
print(table1[["arrival_time", "departure_time"]].head())

# Check whether both columns exist separately
print("\nColumns:")
print(table1.columns.tolist())

# Count rows where column1 and column2 have the same value
same_value_count = (table1["arrival_time"] == table1["departure_time"]).sum()

print("\nRows where arrival_time equals departure_time:",
      same_value_count)

diff_value_count = (table1["arrival_time"] != table1["departure_time"]).sum()

print("\nRows where arrival_time is different from departure_time:",
      diff_value_count)
