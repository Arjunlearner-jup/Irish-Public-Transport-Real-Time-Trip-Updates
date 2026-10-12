import pandas as pd
from pathlib import Path

# Files

static_file = Path("GTFS_Static")/ "trips.txt"
realtime_file = Path("data_clean")/ "trip_updates_one_row_per_trip.csv"
output_file = Path("data_clean")/ "static_realtime_merged.csv"

# Read IDs as strings
static = pd.read_csv(static_file, dtype=str)
realtime = pd.read_csv(realtime_file, dtype=str)

# Clean the join key
static["trip_id"] = static["trip_id"].str.strip()
realtime["trip_id"] = realtime["trip_id"].str.strip()

# Merge records with the same trip_id
merged = realtime.merge(
    static,
    on="trip_id",
    how="inner",  # Keep only trip_ids present in both files
    suffixes=("_realtime", "_static"),
    validate="one_to_one"
)

# Rename route_id_realtime to route_id
merged = merged.rename(columns={"route_id_realtime": "route_id"})

# Compare route IDs, since both tables contain route_id
merged["route_id_matches"] = (
    merged["route_id"] == merged["route_id_static"]
)

# Save
merged.to_csv(output_file, index=False)

print(f"Rows in merged table: {len(merged)}")
print(f"Saved to: {output_file}")
print(merged.head())

