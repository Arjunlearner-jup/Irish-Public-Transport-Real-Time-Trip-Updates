import pandas as pd
import json
from pathlib import Path

input_file = Path("data_clean")/ "final_clean.csv"
df = pd.read_csv(input_file)

output_file = Path("data_clean")/ "trip_updates_one_row_per_trip.csv"
 

df = pd.read_csv(input_file, dtype=str)

# Each entry in stop_updates is one complete original row.
# Sorting by stop_sequence keeps stops in trip order.
df["stop_sequence_sort"] = pd.to_numeric(df["stop_sequence"], errors="coerce")
df = df.sort_values(["trip_id", "stop_sequence_sort"])

# Fields that describe a stop update
stop_columns = [
    "stop_sequence",
    "stop_id",
    "arrival_delay",
    "departure_delay",
]

# Trip-level fields should normally be consistent across rows of the same trip
trip_columns = [
    "entity_id",
    "route_id",
    "trip_start_time",
    "trip_start_date",
    "trip_update_timestamp",
]

rows = []

for trip_id, group in df.groupby("trip_id", sort=False):
    # Store each stop's related values together as one record
    stop_updates = group[stop_columns].to_dict(orient="records")

    # Keep one copy of fields that should be constant for this trip
    row = {"trip_id": trip_id}
    for col in trip_columns:
        row[col] = group[col].iloc[0]

    row["stop_update_count"] = len(stop_updates)
    row["stop_updates"] = json.dumps(stop_updates)

    rows.append(row)

grouped = pd.DataFrame(rows)
grouped.to_csv(output_file, index=False)

print(f"Saved {len(grouped)} trips to {output_file}")