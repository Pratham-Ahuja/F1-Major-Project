import pandas as pd
import numpy as np
from typing import Optional
from src.state.race_state import RaceState


# =========================================================
# Feature Builder — PHASE 6 (FINAL & COMPLETE)
# =========================================================

def build_feature_vector(
    laps_df: pd.DataFrame,
    degradation_df: pd.DataFrame,
    total_laps_allowed: int,
    teammate_map: dict | None = None,
    race_state: Optional[RaceState] = None
) -> pd.DataFrame:

    # -----------------------------------------------------
    # Safety checks
    # -----------------------------------------------------
    required_cols = [
        "Driver", "LapNumber", "Position", "LapTimeSeconds",
        "Compound", "TyreLife", "Stint",
        "RollingMean_3", "RollingMean_5", "RollingMean_7",
        "PaceDelta_3",
        "GapAhead", "GapBehind", "InTraffic",
        "AirTemp", "TrackTemp", "Rainfall"
    ]

    for col in required_cols:
        if col not in laps_df.columns:
            raise ValueError(f"Missing required column: {col}")

    if "DegradationRate_sec_per_lap" not in degradation_df.columns:
        raise ValueError("Missing DegradationRate_sec_per_lap in degradation_df")

    df = laps_df.copy()

    # -----------------------------------------------------
    # STEP 6.2 — Core race context features
    # -----------------------------------------------------
    df["CurrentPosition"] = df["Position"]
    df["LapsRemaining"] = total_laps_allowed - df["LapNumber"]
    df["IsNewTyre"] = df["TyreLife"] == 1

    # Merge degradation rate
    df = df.merge(
        degradation_df[
            ["Driver", "Stint", "DegradationRate_sec_per_lap"]
        ],
        on=["Driver", "Stint"],
        how="left"
    )

    # -----------------------------------------------------
    # STEP 6.3 — Tyre & weather refinements
    # -----------------------------------------------------
    df["MaxTyreLifeInStint"] = (
        df.groupby(["Driver", "Stint"])["TyreLife"].transform("max")
    )

    df["TyreLifePctUsed"] = df["TyreLife"] / df["MaxTyreLifeInStint"]
    df["LateStintFlag"] = df["TyreLifePctUsed"] > 0.7
    df["HighTrackTempFlag"] = df["TrackTemp"] > 45
    df["RainRiskFlag"] = df["Rainfall"] > 0

    df["TyreWeatherRiskScore"] = (
        df["LateStintFlag"].astype(int)
        + df["HighTrackTempFlag"].astype(int)
        + df["RainRiskFlag"].astype(int)
    )

    # -----------------------------------------------------
    # STEP 6.4 — Position-loss estimation
    # -----------------------------------------------------
    df["EstimatedPositionLossIfPit"] = (
        df.groupby("LapNumber")["GapBehind"]
        .transform(lambda x: (x < 5.0).sum())
    )

    # -----------------------------------------------------
    # STEP 6.5 — Teammate features
    # -----------------------------------------------------
    df["TeammateAhead"] = False
    df["TeammateGap"] = np.nan

    if teammate_map is not None:
        for lap, lap_df in df.groupby("LapNumber"):
            for idx, row in lap_df.iterrows():
                teammate = teammate_map.get(row["Driver"])
                if teammate is None:
                    continue

                teammate_row = lap_df[lap_df["Driver"] == teammate]
                if teammate_row.empty:
                    continue

                df.at[idx, "TeammateAhead"] = (
                    teammate_row["Position"].iloc[0] < row["Position"]
                )
                df.at[idx, "TeammateGap"] = abs(
                    teammate_row["LapTimeSeconds"].iloc[0]
                    - row["LapTimeSeconds"]
                )

    # -----------------------------------------------------
    # Optional single-lap mode
    # -----------------------------------------------------
    if race_state is not None:
        df = df[df["LapNumber"] == race_state.current_lap]

    # -----------------------------------------------------
    # ⭐ IMPORTANT — KEEP LapNumber for RaceLoop filtering
    # -----------------------------------------------------
    feature_columns = [
        "LapNumber",          # ⭐ REQUIRED for RaceLoop
        "CurrentPosition",
        "LapsRemaining",
        "TyreLife",
        "Stint",
        "IsNewTyre",
        "TyreLifePctUsed",
        "LateStintFlag",
        "LapTimeSeconds",
        "RollingMean_3",
        "RollingMean_5",
        "RollingMean_7",
        "PaceDelta_3",
        "DegradationRate_sec_per_lap",
        "AirTemp",
        "TrackTemp",
        "Rainfall",
        "HighTrackTempFlag",
        "RainRiskFlag",
        "GapAhead",
        "GapBehind",
        "InTraffic",
        "EstimatedPositionLossIfPit",
        "TeammateAhead",
        "TeammateGap",
        "TyreWeatherRiskScore"
    ]

    return df[feature_columns].copy()