import os
import pandas as pd


# ============================================================
# PROCESS RAW LAPS DATA
# ============================================================

def process_raw_laps(
    laps_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    final_max_laps: int,
    start_lap: int,
    end_lap: int
) -> pd.DataFrame:
    """
    Cleans and prepares lap-level dataset.

    Inputs:
    - laps_df: session.laps dataframe
    - weather_df: session.weather_data dataframe
    - final_max_laps: user provided total race laps
    - start_lap: user chosen start lap
    - end_lap: user chosen end lap

    Returns:
    - processed pandas DataFrame
    """

    # -------------------------------
    # Copy
    # -------------------------------
    laps_df = laps_df.copy()
    weather_df = weather_df.copy()

    # -------------------------------
    # Keep only required lap range
    # -------------------------------
    laps_df = laps_df[
        (laps_df["LapNumber"] >= start_lap) &
        (laps_df["LapNumber"] <= end_lap)
    ]

    # -------------------------------
    # Select useful columns
    # -------------------------------
    laps_df = laps_df[[
        "Driver",
        "LapNumber",
        "LapTime",
        "Position",
        "Compound",
        "TyreLife",
        "Stint"
    ]]

    # -------------------------------
    # Convert lap time to seconds
    # -------------------------------
    laps_df["LapTimeSeconds"] = (
        laps_df["LapTime"].dt.total_seconds()
    )

    laps_df.drop(columns=["LapTime"], inplace=True)

    # -------------------------------
    # Fill missing tyre life
    # -------------------------------
    laps_df["TyreLife"] = laps_df["TyreLife"].fillna(0).astype(int)

    # -------------------------------
    # Basic sorting
    # -------------------------------
    laps_df = laps_df.sort_values(
        ["Driver", "LapNumber"]
    )

    # -------------------------------
    # Weather aggregation per lap
    # -------------------------------
    weather_small = weather_df[[
        "AirTemp",
        "TrackTemp",
        "Rainfall"
    ]].mean().to_frame().T

    weather_small["key"] = 1
    laps_df["key"] = 1

    laps_df = laps_df.merge(
        weather_small,
        on="key",
        how="left"
    )

    laps_df.drop(columns=["key"], inplace=True)

    # -------------------------------
    # Enforce maximum laps rule
    # -------------------------------
    laps_df = laps_df[
        laps_df["LapNumber"] <= final_max_laps
    ]

    # -------------------------------
    # Reset index
    # -------------------------------
    laps_df.reset_index(drop=True, inplace=True)

    print("Processed laps shape:", laps_df.shape)

    return laps_df
