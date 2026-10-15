import matplotlib
matplotlib.use("Agg")

import os
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# Traffic & Gap Analysis
# =========================================================

def traffic_gap_analysis(
    laps_df: pd.DataFrame,
    traffic_threshold_sec: float = 1.5,
    output_dir: str = "outputs/analysis/traffic"
):
    """
    Compute simple traffic and gap metrics using lap-level data.

    Assumptions (simple, deterministic):
    - Gaps are approximated using lap-time differences between
      adjacent positions on the same lap.
    - Traffic is flagged if gap to car ahead < traffic_threshold_sec.

    Returns:
    - laps_with_gaps_df
    - driver_summary_df
    """

    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------
    # Safety checks
    # -----------------------------------------------------
    required_cols = [
        "Driver",
        "LapNumber",
        "Position",
        "LapTimeSeconds"
    ]

    for col in required_cols:
        if col not in laps_df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = laps_df.copy()

    # -----------------------------------------------------
    # Compute gaps per lap (simple approximation)
    # -----------------------------------------------------
    df = df.sort_values(["LapNumber", "Position"])

    df["GapAhead"] = None
    df["GapBehind"] = None

    for lap, df_lap in df.groupby("LapNumber"):
        df_lap = df_lap.sort_values("Position")

        lap_times = df_lap["LapTimeSeconds"].values
        positions = df_lap.index.values

        # Gap to car ahead
        for i in range(1, len(df_lap)):
            gap = lap_times[i] - lap_times[i - 1]
            df.loc[positions[i], "GapAhead"] = gap

        # Gap to car behind
        for i in range(0, len(df_lap) - 1):
            gap = lap_times[i + 1] - lap_times[i]
            df.loc[positions[i], "GapBehind"] = gap

    df["GapAhead"] = df["GapAhead"].astype(float)
    df["GapBehind"] = df["GapBehind"].astype(float)

    # -----------------------------------------------------
    # Traffic flag
    # -----------------------------------------------------
    df["InTraffic"] = df["GapAhead"].apply(
        lambda x: True if pd.notna(x) and x < traffic_threshold_sec else False
    )

    # -----------------------------------------------------
    # Per-driver summary
    # -----------------------------------------------------
    driver_summary_df = (
        df.groupby("Driver")
        .agg(
            LapsInTraffic=("InTraffic", "mean"),
            MeanGapAhead=("GapAhead", "mean"),
            MeanGapBehind=("GapBehind", "mean"),
            TotalLaps=("LapNumber", "count")
        )
        .reset_index()
    )

    driver_summary_df["PctLapsInTraffic"] = (
        driver_summary_df["LapsInTraffic"] * 100
    )

    # -----------------------------------------------------
    # Plots: GapAhead vs LapNumber per driver
    # -----------------------------------------------------
    for driver, df_driver in df.groupby("Driver"):

        if df_driver["GapAhead"].notna().sum() < 3:
            continue

        plt.figure(figsize=(9, 5))
        plt.plot(
            df_driver["LapNumber"],
            df_driver["GapAhead"],
            marker="o",
            linestyle="-",
            linewidth=1
        )
        plt.axhline(
            traffic_threshold_sec,
            color="red",
            linestyle="--",
            label="Traffic Threshold"
        )

        plt.xlabel("Lap Number")
        plt.ylabel("Gap Ahead (seconds)")
        plt.title(f"{driver} - Gap Ahead vs Lap")
        plt.legend()
        plt.grid(True)

        filename = f"{driver}_gap_ahead.png"
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

    return df, driver_summary_df
