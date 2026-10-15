import fastf1

from src.ingestion.load_raw_data import load_race_session
from src.ingestion.process_raw_data import process_raw_laps

from src.analysis.pace_analysis import rolling_pace_analysis
from src.analysis.traffic_analysis import traffic_gap_analysis
from src.analysis.tyre_degradation import tyre_degradation_analysis

from src.features.feature_builder import build_feature_vector

from src.models.pit_decision_model import train_advanced_model
from src.models.train_model import save_model

from src.modes.mode_manager import ModeManager


# =========================================================
# USER INPUTS
# =========================================================
def get_user_inputs():
    print("\n=== F1 AI STRATEGY SYSTEM ===\n")

    year = int(input("Enter season year (e.g. 2023): "))
    gp = input("Enter Grand Prix name (e.g. British Grand Prix): ")
    driver = input("Enter driver code (e.g. VER): ").upper()

    circuit_len = float(input("Enter circuit length (km): "))
    total_laps = int(input("Enter total race laps for this GP: "))

    start_lap = int(input("Start lap for strategy system: "))
    end_lap = int(input("End lap for strategy system: "))

    mode = input("Mode (live / replay / research): ").lower()

    return year, gp, driver, circuit_len, total_laps, start_lap, end_lap, mode


# =========================================================
# MAIN PIPELINE
# =========================================================
def main():

    year, gp, driver, circuit_len, total_laps, start_lap, end_lap, mode = get_user_inputs()

    # -----------------------------------------------------
    # 1. LOAD SESSION
    # -----------------------------------------------------
    session = load_race_session(year, gp)
    laps_df = session.laps
    weather_df = session.weather_data

    # -----------------------------------------------------
    # 2. PROCESS RAW DATA
    # -----------------------------------------------------
    processed_laps_df = process_raw_laps(
        laps_df,
        weather_df,
        total_laps,
        start_lap,
        end_lap
    )

    print("Processed laps shape (all drivers):", processed_laps_df.shape)

    # =====================================================
    # STEP 7 FIX — DRIVER FILTERING
    # =====================================================
    processed_laps_df = processed_laps_df[
        processed_laps_df["Driver"] == driver
    ].copy()

    processed_laps_df = processed_laps_df.sort_values("LapNumber").reset_index(drop=True)

    print("\nDriver selected:", driver)
    print("Driver laps after filtering:", processed_laps_df.shape)

    # -----------------------------------------------------
    # 3. ANALYSIS
    # -----------------------------------------------------
    processed_laps_df = rolling_pace_analysis(processed_laps_df)
    processed_laps_df, _ = traffic_gap_analysis(processed_laps_df)
    degradation_df, _ = tyre_degradation_analysis(processed_laps_df)

    # -----------------------------------------------------
    # 4. FEATURES
    # -----------------------------------------------------
    features_df = build_feature_vector(
        processed_laps_df,
        degradation_df,
        total_laps
    )

    print("Feature dataset shape:", features_df.shape)

    # -----------------------------------------------------
    # 5. TRAIN MODEL
    # -----------------------------------------------------
    model, _ = train_advanced_model(features_df)
    save_model(model, "rf_pit_model")

    # -----------------------------------------------------
    # 6. MODE CONTROLLER
    # -----------------------------------------------------
    manager = ModeManager(
        mode=mode,
        features_df=features_df,
        trained_model=model,
        total_laps=total_laps,
        circuit_length_km=circuit_len,
        start_lap=start_lap,
        end_lap=end_lap
    )

    manager.run()


if __name__ == "__main__":
    main()