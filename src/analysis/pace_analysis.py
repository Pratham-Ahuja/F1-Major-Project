import matplotlib
matplotlib.use("Agg")

import os
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# Rolling Pace Analysis
# =========================================================

def rolling_pace_analysis(
    laps_df: pd.DataFrame,
    output_dir: str = "outputs/analysis/pace"
):
    """
    Compute rolling pace metrics for drivers.

    Outputs:
    - Rolling mean lap times (3, 5, 7 laps)
    - Pace delta (lap time - rolling mean)
    - Per-driver pace plots

    Returns:
    - laps_with_pace_df
    """

    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------
    # Safety checks
    # -----------------------------------------------------
    required_cols = [
        "Driver",
        "LapNumber",
        "LapTimeSeconds"
    ]

    for col in required_cols:
        if col not in laps_df.columns:
            raise ValueError(f"Missing required column: {col}")

    laps_df = laps_df.sort_values(["Driver", "LapNumber"]).copy()

    # -----------------------------------------------------
    # Rolling windows
    # -----------------------------------------------------
    windows = [3, 5, 7]

    for w in windows:
        laps_df[f"RollingMean_{w}"] = (
            laps_df
            .groupby("Driver")["LapTimeSeconds"]
            .transform(lambda x: x.rolling(window=w, min_periods=1).mean())
        )

        laps_df[f"PaceDelta_{w}"] = (
            laps_df["LapTimeSeconds"] - laps_df[f"RollingMean_{w}"]
        )

    # -----------------------------------------------------
    # Per-driver plots
    # -----------------------------------------------------
    for driver, df_driver in laps_df.groupby("Driver"):

        if len(df_driver) < max(windows):
            continue

        plt.figure(figsize=(10, 6))
        plt.plot(
            df_driver["LapNumber"],
            df_driver["LapTimeSeconds"],
            label="Lap Time",
            linewidth=1.5
        )

        for w in windows:
            plt.plot(
                df_driver["LapNumber"],
                df_driver[f"RollingMean_{w}"],
                label=f"Rolling Mean {w}",
                linestyle="--"
            )

        plt.xlabel("Lap Number")
        plt.ylabel("Lap Time (seconds)")
        plt.title(f"{driver} - Rolling Pace Analysis")
        plt.legend()
        plt.grid(True)

        filename = f"{driver}_rolling_pace.png"
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

    return laps_df
