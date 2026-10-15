import pandas as pd

from src.live_loop.race_loop import RaceLoop


# =========================================================
# PHASE 13.1 — REPLAY-BASED VALIDATION
# =========================================================

def run_replay_validation(
    processed_laps_df: pd.DataFrame,
    degradation_df: pd.DataFrame,
    model,
    driver_id: str,
    total_laps_allowed: int,
    lap_distance_km: float,
    teammate_map: dict | None = None
):
    """
    Run full system in replay mode and log AI decisions
    against real race events.
    """

    print("\n=== STARTING REPLAY-BASED VALIDATION ===\n")

    race_loop = RaceLoop(
        processed_laps_df=processed_laps_df,
        degradation_df=degradation_df,
        model=model,
        driver_id=driver_id,
        total_laps_allowed=total_laps_allowed,
        lap_distance_km=lap_distance_km,
        strategy_type="BALANCED",
        teammate_map=teammate_map
    )

    decision_logs = []

    while not race_loop.race_state.is_race_complete():

        lap = race_loop.race_state.current_lap

        # -----------------------------
        # Extract real pit info
        # -----------------------------
        lap_df = processed_laps_df[
            processed_laps_df["LapNumber"] == lap
        ]

        driver_row = lap_df[
            lap_df["Driver"] == driver_id
        ]

        if driver_row.empty:
            break

        driver_row = driver_row.iloc[0]

        real_pit = bool(driver_row.get("PitInTime"))

        # -----------------------------
        # Run one lap of the system
        # -----------------------------
        race_loop.run()

        last_state = race_loop.race_state.history[-1]

        decision_logs.append({
            "Lap": lap,
            "AI_Decision": last_state.get("decision"),
            "AI_Confidence": last_state.get("confidence"),
            "AI_Strategy": last_state.get("strategy_type"),
            "Real_Pit": real_pit
        })

    decision_df = pd.DataFrame(decision_logs)

    print("\n=== REPLAY VALIDATION COMPLETE ===")
    print(decision_df.head())

    return decision_df
