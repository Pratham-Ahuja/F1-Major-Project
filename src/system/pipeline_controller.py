# =========================================================
# PIPELINE CONTROLLER
# =========================================================

import pandas as pd
import pickle
import fastf1
import numpy as np

from src.live_loop.race_loop import RaceLoop


class PipelineController:
    """
    Central controller responsible for preparing inputs
    and launching the race simulation pipeline.
    """

    def __init__(self):
        pass


    # -----------------------------------------------------
    # LOAD RACE DATA
    # -----------------------------------------------------

    def load_race_features(self, season, race, driver, total_laps):

        print("Loading race dataset...")

        try:

            # ---------------------------------------------
            # Load FastF1 race session
            # ---------------------------------------------
            session = fastf1.get_session(season, race, "R")
            session.load()

            laps = session.laps.pick_driver(driver)

            laps = laps[[
                "LapNumber",
                "Compound",
                "TyreLife",
                "Stint",
                "Position",
                "LapTime"
            ]].copy()

            laps.rename(columns={
                "Compound": "TyreCompound",
                "Position": "CurrentPosition"
            }, inplace=True)

            laps["LapTime"] = laps["LapTime"].dt.total_seconds()

            # ------------------------------------------------
            # REMOVE INVALID LAPS (safety cars, pit laps etc)
            # ------------------------------------------------

            laps = laps.dropna(subset=["LapTime"])

            # ------------------------------------------------
            # GAP ESTIMATION (better calculation)
            # ------------------------------------------------

            laps["GapAhead"] = laps["LapTime"].diff().abs()
            laps["GapBehind"] = laps["LapTime"].diff(-1).abs()

            laps["GapAhead"] = laps["GapAhead"].fillna(2.5)
            laps["GapBehind"] = laps["GapBehind"].fillna(3.0)

            # ------------------------------------------------
            # WEATHER FEATURES
            # ------------------------------------------------

            weather = session.weather_data

            air_temp = weather["AirTemp"].mean() if not weather.empty else 28
            track_temp = weather["TrackTemp"].mean() if not weather.empty else 42
            rainfall = weather["Rainfall"].mean() if not weather.empty else 0

            laps["AirTemp"] = air_temp
            laps["TrackTemp"] = track_temp
            laps["Rainfall"] = rainfall

            # ------------------------------------------------
            # ROLLING PACE METRICS
            # ------------------------------------------------

            laps["RollingMean_3"] = laps["LapTime"].rolling(3).mean().bfill()
            laps["RollingMean_5"] = laps["LapTime"].rolling(5).mean().bfill()
            laps["RollingMean_7"] = laps["LapTime"].rolling(7).mean().bfill()

            laps["PaceDelta_3"] = laps["LapTime"] - laps["RollingMean_3"]

            # ------------------------------------------------
            # TYRE DEGRADATION ESTIMATE
            # ------------------------------------------------

            laps["DegradationRate_sec_per_lap"] = laps["LapTime"].diff().abs().fillna(0)

            # ------------------------------------------------
            # TRAFFIC ESTIMATION
            # ------------------------------------------------

            laps["InTraffic"] = laps["GapAhead"] < 1.5

            laps["TeammateAhead"] = False
            laps["TeammateGap"] = 5

            # ------------------------------------------------
            # PIT LOSS ESTIMATE
            # ------------------------------------------------

            laps["EstimatedPositionLossIfPit"] = 3

            # ------------------------------------------------
            # WEATHER RISK
            # ------------------------------------------------

            laps["TyreWeatherRiskScore"] = np.where(
                laps["Rainfall"] > 0,
                3,
                1
            )

            # ------------------------------------------------
            # FIX POSITION ISSUE
            # ------------------------------------------------
            # Sometimes FastF1 keeps position constant
            # We simulate small fluctuations

            position_noise = np.random.choice(
                [-1, 0, 1],
                size=len(laps),
                p=[0.1, 0.8, 0.1]
            )

            laps["CurrentPosition"] = (
                laps["CurrentPosition"] + position_noise
            ).clip(lower=1)

            # ------------------------------------------------
            # LIMIT TO REQUESTED LAPS
            # ------------------------------------------------

            features_df = laps.head(total_laps)

            print("FastF1 telemetry loaded successfully.")

            return features_df

        except Exception as e:

            print("WARNING: FastF1 data unavailable, using fallback synthetic data.")
            print(e)

            # ---------------------------------------------
            # FALLBACK synthetic dataset
            # ---------------------------------------------

            data = {
                "LapNumber": list(range(1, total_laps + 1)),
                "TyreCompound": ["MEDIUM"] * total_laps,
                "TyreLife": list(range(1, total_laps + 1)),
                "Stint": [1] * total_laps,
                "CurrentPosition": [5] * total_laps,

                "GapAhead": [2.5] * total_laps,
                "GapBehind": [3.0] * total_laps,
                "EstimatedPositionLossIfPit": [3] * total_laps,
                "AirTemp": [28] * total_laps,
                "TrackTemp": [42] * total_laps,
                "Rainfall": [0] * total_laps,
                "RollingMean_3": [90] * total_laps,
                "RollingMean_5": [90] * total_laps,
                "RollingMean_7": [90] * total_laps,
                "PaceDelta_3": [0.2] * total_laps,
                "DegradationRate_sec_per_lap": [0.15] * total_laps,
                "InTraffic": [False] * total_laps,
                "TeammateAhead": [False] * total_laps,
                "TeammateGap": [5] * total_laps,
                "TyreWeatherRiskScore": [1] * total_laps,
            }

            return pd.DataFrame(data)


    # -----------------------------------------------------
    # LOAD MODEL
    # -----------------------------------------------------

    def load_model(self):

        print("Loading trained pit prediction model...")

        model_path = "models_artifacts/rf_pit_model.pkl"

        try:

            with open(model_path, "rb") as f:
                trained_model = pickle.load(f)

            print("Model loaded successfully.")

        except Exception:

            print("WARNING: Model not available. Running without ML model.")

            trained_model = None

        return trained_model


    # -----------------------------------------------------
    # BUILD RACE LOOP
    # -----------------------------------------------------

    def build_race_loop(self, config):

        season = config["season"]
        race = config["race"]
        driver = config["driver"]

        total_laps = int(config["total_laps"])
        circuit_len = float(config["circuit_len"])
        start_lap = int(config["start_lap"])
        end_lap = int(config["end_lap"])

        features_df = self.load_race_features(
            season,
            race,
            driver,
            total_laps
        )

        trained_model = self.load_model()

        race_loop = RaceLoop(
            features_df=features_df,
            trained_model=trained_model,
            total_laps=total_laps,
            circuit_length_km=circuit_len,
            start_lap=start_lap,
            end_lap=end_lap,
            config=None
        )

        return race_loop


    # -----------------------------------------------------
    # MAIN PIPELINE
    # -----------------------------------------------------

    def run(self, mode, config):

        print("Running strategy pipeline...")

        race_loop = self.build_race_loop(config)

        return race_loop