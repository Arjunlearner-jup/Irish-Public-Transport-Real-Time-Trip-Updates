# Ireland GTFS-Realtime Data Pipeline


## 1. Download Realtime Feed — `1col_pb.py`
  
  This script sends an authenticated GET request to the National Transport Authority GTFS-Realtime API and saves the raw Protocol Buffers response.

### Functions used

- `requests.get()`
- `print()`
- `response.raise_for_status()`
- `folder.mkdir()`
- `datetime.now()`
- `.strftime()`
- `file_path.write_bytes()`
- `len()`

## 2. Parse GTFS-Realtime Feed — `2ETL.py`
  
  This script finds the newest `.pb` file, parses it using the GTFS-Realtime Python bindings, and converts vehicle positions, trip updates, and service alerts into CSV files.

### Functions used

- `Path()`
- `OUTPUT_DIR.mkdir()`
- `INPUT_DIR.glob()`
- `sorted()`
- `file.stat()`
- `lambda`
- `raise FileNotFoundError()`
- `gtfs_realtime_pb2.FeedMessage()`
- `latest_file.open()`
- `f.read()`
- `feed.ParseFromString()`
- `entity.HasField()`
- `len()`
- `ts_to_iso()`
- `datetime.fromtimestamp()`
- `.isoformat()`
- `.append()`
- `pd.DataFrame()`
- `df.to_csv()`
- `print()`

### Outputs

```text
data/ireland_realtime_csv/vehicle_positions.csv
data/ireland_realtime_csv/trip_updates.csv
data/ireland_realtime_csv/alerts.csv
```


## 3. Clean Trip Updates — `3clandsave.py`
  
  This script cleans the stop-level trip-update dataset by removing unnecessary columns, blank trip or stop identifiers, and missing numeric delay values.

### Functions used

- `Path()`
- `pd.read_csv()`
- `df.drop()`
- `raise KeyError()`
- `.str.strip()`
- `df.dropna()`
- `.ne()`
- `df.select_dtypes()`
- `.isna()`
- `.any()`
- `df[col].quantile()`
- `df[col].fillna()`
- `output_file.parent.mkdir()`
- `df.to_csv()`
- `len()`
- `print()`

### Output

```text
data_clean/final_clean.csv
```

---
  
## 4. Create One Row Per Trip — `4merge_tripid.py`
  
  This script groups all stop-level updates by `trip_id`, keeps trip-level information once, and stores the stop updates as a JSON array.

### Functions used

- `Path()`
- `pd.read_csv()`
- `pd.to_numeric()`
- `df.sort_values()`
- `df.groupby()`
- `group[stop_columns]`
- `.to_dict()`
- `len()`
- `json.dumps()`
- `rows.append()`
- `pd.DataFrame()`
- `grouped.to_csv()`
- `print()`

### Output

```text
data_clean/trip_updates_one_row_per_trip.csv
```

### Output columns

| Column | Description |
| :--- | :--- |
| `trip_id` | Unique trip identifier |
| `entity_id` | GTFS-Realtime entity ID |
| `route_id` | Route served by the trip |
| `trip_start_time` | Scheduled trip start time |
| `trip_start_date` | Service date |
| `trip_update_timestamp` | Time the trip update was generated |
| `stop_update_count` | Number of stop updates for the trip |
| `stop_updates` | JSON array of stop-level updates |

  ---
  
## 5. Merge Realtime and Static Trips — `5final-static-rt-merged.py`
  
  This script performs an inner join between the realtime trip-level dataset and GTFS Static `trips.txt` using `trip_id`.

### Functions used

- `Path()`
- `pd.read_csv()`
- `.str.strip()`
- `realtime.merge()`
- `merged.rename()`
- `merged.to_csv()`
- `len()`
- `print()`
- `merged.head()`

### Output

```text
data_clean/static_realtime_merged.csv
```

### Join behaviour

| Condition | Result |
|:--- |:--- |
| `trip_id` exists in both files | Rows are merged |
| `trip_id` exists only in realtime data | Row is excluded |
| `trip_id` exists only in static data | Row is excluded |
| Duplicate `trip_id` in either file | Script raises an error |
| Route IDs differ | Row is retained; `route_id_matches` is `False` |
  
  ---
  
## Data Analysis 1 — Trip Match Rate
  
  This script compares the number of realtime trips with the number of trips successfully matched to GTFS Static data.

### Functions used

- `Path()`
- `file_path.exists()`
- `raise FileNotFoundError()`
- `file_path.resolve()`
- `pd.read_csv()`
- `len()`
- `print()`

### Calculation

```python
match_rate = (table2_count / table1_count) * 100
```

### Inputs

```text
data_clean/trip_updates_one_row_per_trip.csv
data_clean/static_realtime_merged.csv
```

---
  
## Data Analysis 2 — Join Stop-Level Data
  
  This script joins cleaned realtime stop-level data with GTFS Static `stop_times.txt` using both `trip_id` and `stop_sequence`.

### Functions used

- `Path()`
- `pd.read_csv()`
- `.str.strip()`
- `.str.lower()`
- `.astype()`
- `pd.to_numeric()`
- `.astype("Int64")`
- `df.dropna()`
- `print()`
- `table1[...].head()`
- `table2[...].head()`
- `set()`
- `len()`
- `.iloc()`
- `table2.merge()`
- `output_file.parent.mkdir()`
- `merged.to_csv()`
- `merged.head()`

### Join keys

```text
trip_id
stop_sequence
```

### Output

```text
Data analysis/final_clean_stop_times_joined.csv
```

### Join behaviour

| Condition | Result |
|:--|:--|
| `trip_id` and `stop_sequence` match | Rows are joined |
| Only `trip_id` matches | Row is excluded |
| Only `stop_sequence` matches | Row is excluded |
| Either join key is missing | Row is removed before merging |
  
  ---
  
## Data Analysis 2.1 — Arrival and Departure Comparison
  
  This script checks how often `arrival_time` equals `departure_time` in the joined static-realtime dataset.

### Functions used

- `Path()`
- `pd.read_csv()`
- `table1[["arrival_time", "departure_time"]]`
- `.head()`
- `print()`
- `table1.columns.tolist()`
- `.sum()`

### Interpretation

| Result | Meaning |
|:--|:--|
| `arrival_time == departure_time` | No dwell time is scheduled at the stop |
| `arrival_time != departure_time` | The schedule allows dwell time at the stop |
  
  ---
  
## Data Analysis 2.2 — Predicted Arrival and Departure Times
  
  This script combines scheduled GTFS Static times with realtime delay values to calculate predicted arrival and departure datetimes.

### Functions used

- `Path()`
- `pd.read_csv()`
- `.astype()`
- `.str.strip()`
- `pd.to_numeric()`
- `pd.to_datetime()`
- `pd.to_timedelta()`
- `.dt.strftime()`
- `.isna()`
- `.sum()`
- `df.to_csv()`
- `df[[...]].head()`
- `len()`
- `print()`

### Calculations

| Output field | Formula |
|:--|:--|
| `scheduled_arrival_datetime` | `trip_start_date + scheduled_arrival_time` |
| `predicted_arrival_datetime` | `scheduled_arrival_datetime + arrival_delay_seconds` |
| `scheduled_departure_datetime` | `trip_start_date + scheduled_departure_time` |
| `predicted_departure_datetime` | `scheduled_departure_datetime + departure_delay_seconds` |
| `arrival_delay_minutes` | `arrival_delay_seconds / 60` |
| `departure_delay_minutes` | `departure_delay_seconds / 60` |
  
## Output
  
  ```text
Data analysis/schedule_vs_prediction_analysis.csv
```

