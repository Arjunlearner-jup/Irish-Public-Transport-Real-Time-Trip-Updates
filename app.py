import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from pathlib import Path

st.title("Schedule vs Prediction: Arrival and Delay Distributions")

# CSV path is relative to the folder where you run Streamlit
input_file = Path("Data analysis") / "schedule_vs_prediction_analysis.csv"

if not input_file.exists():
    st.error(f"File not found: {input_file.resolve()}")
    st.stop()

df = pd.read_csv(input_file)

delay_columns = [
    ("arrival_delay_seconds", "Arrival delay", "steelblue"),
    ("departure_delay_seconds", "Departure delay", "darkorange"),
]

for column, label, color in delay_columns:
    if column not in df.columns:
        st.warning(f"Column not found in CSV: {column}")
        continue

    # Convert seconds to minutes; non-numeric values become missing
    delay_minutes = pd.to_numeric(df[column], errors="coerce") / 60

    # Ignore missing values and cap values for display
    plot_data = delay_minutes.dropna().clip(lower=-30, upper=60)

    if plot_data.empty:
        st.warning(f"No valid values to plot for {label.lower()}.")
        continue

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(plot_data, bins=50, color=color, edgecolor="black")
    ax.axvline(
        0,
        color="red",
        linestyle="--",
        linewidth=2,
        label="On schedule",
    )

    ax.set_title(f"{label} Distribution")
    ax.set_xlabel(f"Predicted {label.lower()} (minutes)")
    ax.set_ylabel("Number of stop predictions")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)