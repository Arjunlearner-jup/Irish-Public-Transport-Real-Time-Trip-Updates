from pathlib import Path

import pandas as pd
import streamlit as st


# -----------------------------------------
# 1. Page configuration
# -----------------------------------------
st.set_page_config(
    page_title="GTFS Trip Match Analysis",
    page_icon="🚌",
    layout="wide",
)

st.title("GTFS Trip Match Analysis")
st.write(
    "Compare the number of realtime trips with the number "
    "successfully matched to GTFS Static data."
)


# -----------------------------------------
# 2. Input file paths
# -----------------------------------------

table1_file = Path("data_clean") / "trip_updates_one_row_per_trip.csv"
table2_file = Path("data_clean") / "static_realtime_merged.csv"

# -----------------------------------------
# 3. Check that both files exist
# -----------------------------------------
for file_path in [table1_file, table2_file]:
    if not file_path.exists():
        st.error(f"File not found: {file_path.resolve()}")
        st.stop()


# -----------------------------------------
# 4. Load the CSV files
# -----------------------------------------
try:
    table1 = pd.read_csv(table1_file)
    table2 = pd.read_csv(table2_file)
except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
    st.error(f"Could not read the CSV files: {error}")
    st.stop()


# -----------------------------------------
# 5. Count rows
# -----------------------------------------
table1_count = len(table1)
table2_count = len(table2)

col1, col2 = st.columns(2)

with col1:
    st.metric("Realtime trips — Table 1", f"{table1_count:,}")

with col2:
    st.metric("Matched trips — Table 2", f"{table2_count:,}")


# -----------------------------------------
# 6. Calculate the match rate
# -----------------------------------------
st.subheader("Trip match rate")

if table1_count == 0:
    st.warning("Cannot calculate result: table1 has 0 rows.")
else:
    result = (table2_count / table1_count) * 100

    st.metric("Match rate", f"{result:.2f}%")

    st.write(
        f"Calculation: ({table2_count:,} / {table1_count:,}) "
        f"× 100 = {result:.2f}%"
    )

    if table2_count > table1_count:
        st.warning(
            "The merged table contains more rows than the realtime "
            "table. Check for duplicate trip IDs or duplicated join results."
        )

st.caption(
    "This is a row-count comparison. It represents a trip match rate "
    "only when Table 1 contains one row per trip and Table 2 is its "
    "corresponding merged result without duplicate trip rows."
)


# -----------------------------------------
# 7. Optional data previews
# -----------------------------------------
with st.expander("Preview realtime trip data"):
    st.dataframe(table1.head(10), use_container_width=True)

with st.expander("Preview merged static–realtime data"):
    st.dataframe(table2.head(10), use_container_width=True)