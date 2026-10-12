# Irish Public Transport Real-Time Trip Updates

## Project overview

This project processes Ireland’s public transport GTFS-Realtime feed and compares real-time trip and stop updates with the static GTFS timetable. It downloads and parses the protobuf feed, cleans and reshapes trip updates, matches them to static GTFS files, calculates delay-adjusted arrival and departure times, and visualizes delay distributions in a Streamlit app.

The National Transport Authority (NTA) real-time feed requires an API key. 

## Workflow
1. **Available/ manually downloaded:**   Manually download GTFS static files. Available as a zip file
2. **Download the feed:** request the GTFS-Realtime protobuf feed and save a timestamped `.pb` file in `data/ireland_realtime/`.
3. **Parse and flatten:** parse the latest protobuf file and export vehicle positions, trip updates, and service alerts as CSV files in `data/ireland_realtime_csv/`.
4. **Clean trip updates:** remove unused fields, discard records without `trip_id` or `stop_id`, and handle missing numeric values. Output: `data_clean/final_clean.csv`.
5. **Group updates by trip:** sort stop updates by `stop_sequence` and package stop-level records as JSON. Output: `data_clean/trip_updates_one_row_per_trip.csv`.
6. **Match trips to the static schedule:** join grouped real-time trips to `trips.txt` using `trip_id`. Output: `data_clean/static_realtime_merged.csv`.
7. **Data analysis 1:** calculate the percentage of real-time trips matched to the static schedule.
8. **Join stop updates:** join cleaned real-time stop records to `stop_times.txt` using `trip_id` and `stop_sequence`.
9. **Data analysis 2:** calculate delay-adjusted arrival and departure times and save the analysis table.
10. **Visualize:** run the Streamlit dashboard to view delay distributions.

## Execution order

Run the scripts in sequence from the project root. The output folders and CSV files are created by the scripts when they run, as indicated by their code. Static GTFS input files and the scripts themselves must already be in the locations expected by the code.

| Order | Script | Purpose |
|---:|---|---|
| 1 | `col_pb.py` | Download the NTA realtime feed as a timestamped protobuf file. |
| 2 | `ETL.py` | Parse the protobuf file and export feed entities to CSV. |
| 3 | `clandsave.py` | Clean trip updates and save `final_clean.csv`. |
| 4 | `merge_tripid.py` | Group stop updates into one row per trip. |
| 5 | `final-static-rt-merged.py` | Match real-time trips to static `trips.txt`. |
| 6 | `Data_analysis 1.py` | Calculate trip-match coverage. |
| 7 | `Data_analysis 2.py` | Join real-time stop updates to static stop times. |
| 8 | `Data_analysis 2.1.py` | Check scheduled arrival and departure time values. |
| 9 | `Data_analysis 2.2.py` | Calculate predicted times and write the analysis CSV. |
| 10 | `app.py` | Streamlit dashboard for arrival and departure delay histograms. |

Use the exact filenames present on your computer. Some names in the original list were shown as links or had inconsistent spelling (for example, `Sreamlit`); this README assumes the dashboard file is named `app.py`.

## Data analysis 1: Trip-match coverage

This analysis estimates the percentage of real-time trips represented in the static–realtime merged table:

```text
match percentage = (matched trip rows / real-time trip rows) * 100
```

The merge is an inner join on `trip_id`, so only matching IDs remain. This percentage describes match coverage; it is not a delay, punctuality, or prediction-accuracy score. Check for duplicate trip IDs so row counts represent trips as intended.

## Data analysis 2: Schedule versus prediction

This is a stop-level analysis. It matches each real-time stop update to a scheduled stop using `trip_id` and `stop_sequence`, then calculates:

```text
predicted arrival   = scheduled arrival   + arrival delay
predicted departure = scheduled departure + departure delay
```

Delays are represented in seconds and are also converted to minutes for analysis and plotting. The Streamlit dashboard displays arrival and departure delay distributions; the zero line marks no reported delay. The histogram clips plotted values to −30 through +60 minutes, so delays outside that range appear at the boundary.

The analysis creates delay-adjusted predicted times. It does not assess prediction accuracy against actual observed arrival or departure times; that requires independent observations of actual times.

## Requirements and inputs

- Python and the packages imported by the scripts: `requests`, `pandas`, `numpy`, `google-transit`, `matplotlib`, and `streamlit`.
- NTA GTFS-Realtime API access and an API key.
- Static GTFS files, including `trips.txt` and `stop_times.txt`, placed where the scripts expect them (the examples use `GTFS_Realtime/`).

Install the Python packages with:

```bash
python -m pip install requests pandas numpy google-transit matplotlib streamlit
```

## Generated outputs

The scripts create their output folders and files when executed, assuming each prior step completes successfully. Typical outputs include:

- `data/ireland_realtime/gtfsr_<timestamp>.pb`
- `data/ireland_realtime_csv/vehicle_positions.csv`
- `data/ireland_realtime_csv/trip_updates.csv`
- `data/ireland_realtime_csv/alerts.csv`
- `data_clean/final_clean.csv`
- `data_clean/trip_updates_one_row_per_trip.csv`
- `data_clean/static_realtime_merged.csv`
- `Data analysis/final_clean_stop_times_joined.csv`
- `Data analysis/schedule_vs_prediction_analysis.csv`

The entity CSVs may only be written when the feed contains that entity type. The prediction-analysis CSV is the input required by the dashboard.

## Run the Streamlit dashboard

Run the command from the project root, replacing `code` if your folder has a different name. If `app.py` is inside the `code` folder:

```bash
python -m streamlit run code/app.py
```

Alternatively, change into the folder containing the app and run it there:

```bash
cd foldername
python -m streamlit run app.py
```

The dashboard code reads this relative path:

```text
Data analysis/schedule_vs_prediction_analysis.csv
```

Therefore, make sure the CSV exists at that path relative to the directory from which Streamlit runs. If `Data analysis` is outside `code_completed`, either run Streamlit from the project root with the first command or update the `input_file` path in `app.py` to match your folder layout. Streamlit prints the local app address in the terminal when it starts.

## Suggested folder layout

```text
project_root/
├── GTFS_Realtime/                     # Static GTFS: trips.txt, stop_times.txt
├── data/                               # Created by feed-download script
│   └── ireland_realtime/
├── data_clean/                         # Created by processing scripts
├── Data analysis/                      # Created by analysis scripts
│   └── schedule_vs_prediction_analysis.csv
└── code/
    ├── col_pb.py
    ├── ETL.py
    ├── clandsave.py
    ├── merge_tripid.py
    ├── final-static-rt-merged.py
    ├── Data_analysis 1.py
    ├── Data_analysis 2.py
    ├── Data_analysis 2.1.py
    ├── Data_analysis 2.2.py
    └── app.py
```

This is an example layout, not a requirement. The actual paths must agree with the `Path(...)` values inside each script. In particular, check whether the analysis output directory is named `Data analysis` relative to the working directory.

## GTFS_Static data is saved as pre-release

The memory size of GTFS Static data was more than 25 mb hence had to save it as a release. Downloading the static data is very important for the project. Save it in the folder GTFS_Static in the project folder.
