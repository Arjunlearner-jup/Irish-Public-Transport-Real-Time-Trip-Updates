import pandas as pd
from pathlib import Path


# Input: table created after joining final_clean.csv with stop_times.csv
input_file = Path("Data analysis") / "final_clean_stop_times_joined.csv"

# Output

output_file = Path("Data analysis") / "schedule_vs_prediction_analysis.csv"

# Load the joined table
df = pd.read_csv(input_file, dtype=str)


# Clean text columns
df["trip_start_date"] = df["trip_start_date"].astype(str).str.strip()

df["arrival_time"] = df["arrival_time"].astype(str).str.strip()
df["departure_time"] = df["departure_time"].astype(str).str.strip()


# Scheduled times come from static stop_times.csv
df["scheduled_arrival_time"] = df["arrival_time"]
df["scheduled_departure_time"] = df["departure_time"]


# Convert real-time delay values to numeric seconds
df["arrival_delay_seconds"] = pd.to_numeric(
    df["arrival_delay"],
    errors="coerce"
)

df["departure_delay_seconds"] = pd.to_numeric(
    df["departure_delay"],
    errors="coerce"
)


# Convert delays to minutes
df["arrival_delay_minutes"] = df["arrival_delay_seconds"] / 60
df["departure_delay_minutes"] = df["departure_delay_seconds"] / 60


# Create full scheduled arrival datetime
# trip_start_date format: YYYYMMDD, for example 20261011
df["scheduled_arrival_datetime"] = pd.to_datetime(
    df["trip_start_date"] + " " + df["scheduled_arrival_time"],
    format="%Y%m%d %H:%M:%S",
    errors="coerce"
)


# Predicted arrival = scheduled arrival + arrival delay in seconds
df["predicted_arrival_datetime"] = (
    df["scheduled_arrival_datetime"]
    + pd.to_timedelta(df["arrival_delay_seconds"], unit="s")
)


# Create full scheduled departure datetime
df["scheduled_departure_datetime"] = pd.to_datetime(
    df["trip_start_date"] + " " + df["scheduled_departure_time"],
    format="%Y%m%d %H:%M:%S",
    errors="coerce"
)


# Predicted departure = scheduled departure + departure delay in seconds
df["predicted_departure_datetime"] = (
    df["scheduled_departure_datetime"]
    + pd.to_timedelta(df["departure_delay_seconds"], unit="s")
)


# Create readable timestamp columns for Excel and CSV output
df["predicted_arrival_time"] = df[
    "predicted_arrival_datetime"
].dt.strftime("%Y-%m-%d %H:%M:%S")

df["predicted_departure_time"] = df[
    "predicted_departure_datetime"
].dt.strftime("%Y-%m-%d %H:%M:%S")


# Diagnostics: confirm the calculation succeeded
print("Missing scheduled arrival datetimes:",
      df["scheduled_arrival_datetime"].isna().sum())

print("Missing scheduled departure datetimes:",
      df["scheduled_departure_datetime"].isna().sum())

print("Missing predicted arrival times:",
      df["predicted_arrival_time"].isna().sum())

print("Missing predicted departure times:",
      df["predicted_departure_time"].isna().sum())


# Save final analysis table
df.to_csv(output_file, index=False)


# Display selected columns
print(
    df[
        [
            "trip_id",
            "stop_sequence",
            "trip_start_date",
            "scheduled_arrival_time",
            "arrival_delay_seconds",
            "predicted_arrival_time",
            "scheduled_departure_time",
            "departure_delay_seconds",
            "predicted_departure_time",
        ]
    ].head(10)
)

print(f"\nRows saved: {len(df)}")
print(f"Saved to: {output_file}")