import matplotlib
matplotlib.use("Agg")

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# =========================================================
# Tyre Degradation Analysis
# =========================================================

def tyre_degradation_analysis(
    laps_df: pd.DataFrame,
    output_dir: str = "outputs/analysis/tyre_degradation"
):
    """
    Perform tyre degradation analysis using processed lap data.

    Outputs:
    - Per-driver degradation plots (LapTime vs TyreLife)
    - Stint-level degradation rates
    - Aggregate compound-level degradation summary

    Returns:
    - stint_degradation_df
    - compound_summary_df
    """

    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------
    # Safety checks
    # -----------------------------------------------------
    required_cols = [
        "Driver",
        "LapNumber",
        "LapTimeSeconds",
        "Compound",
        "TyreLife",
        "Stint"
    ]

    for col in required_cols:
        if col not in laps_df.columns:
            raise ValueError(f"Missing required column: {col}")

    # -----------------------------------------------------
    # 1. Per-driver degradation plots
    # -----------------------------------------------------
    for (driver, compound), df_sub in laps_df.groupby(["Driver", "Compound"]):

        if df_sub["TyreLife"].nunique() < 3:
            continue

        plt.figure(figsize=(8, 5))
        plt.scatter(df_sub["TyreLife"], df_sub["LapTimeSeconds"], alpha=0.6)
        plt.xlabel("Tyre Life (laps)")
        plt.ylabel("Lap Time (seconds)")
        plt.title(f"{driver} - {compound} Tyre Degradation")
        plt.grid(True)

        filename = f"{driver}_{compound}_tyre_degradation.png"
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

    # -----------------------------------------------------
    # 2. Stint-level degradation rate (linear slope)
    # -----------------------------------------------------
    stint_records = []

    for (driver, stint), df_stint in laps_df.groupby(["Driver", "Stint"]):

        if df_stint["TyreLife"].nunique() < 3:
            continue

        x = df_stint["TyreLife"].values
        y = df_stint["LapTimeSeconds"].values

        slope, intercept = np.polyfit(x, y, 1)

        stint_records.append({
            "Driver": driver,
            "Stint": stint,
            "Compound": df_stint["Compound"].iloc[0],
            "DegradationRate_sec_per_lap": slope,
            "MeanLapTime": y.mean(),
            "LapsInStint": len(df_stint)
        })

    stint_degradation_df = pd.DataFrame(stint_records)

    # -----------------------------------------------------
    # 3. Compound-level aggregate summary
    # -----------------------------------------------------
    compound_summary_df = (
        stint_degradation_df
        .groupby("Compound")
        .agg(
            MeanDegradationRate=("DegradationRate_sec_per_lap", "mean"),
            StdDegradationRate=("DegradationRate_sec_per_lap", "std"),
            NumStints=("DegradationRate_sec_per_lap", "count")
        )
        .reset_index()
    )

    return stint_degradation_df, compound_summary_df
