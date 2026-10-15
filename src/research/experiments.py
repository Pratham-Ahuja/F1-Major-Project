import pandas as pd

from src.research.replay_runner import run_replay_validation
from src.research.metrics import compute_pit_metrics
from src.research.decision_logger import log_decisions


# =========================================================
# PHASE 13.3 — EXPERIMENT RUNNER
# =========================================================

def run_experiments(
    processed_laps_df: pd.DataFrame,
    degradation_df: pd.DataFrame,
    baseline_model,
    advanced_model,
    driver_id: str,
    year: int,
    gp_name: str,
    total_laps_allowed: int,
    lap_distance_km: float,
    teammate_map: dict | None = None
):
    """
    Run controlled experiments to validate system components.
    """

    experiment_results = []

    experiments = [
        {
            "name": "Baseline_Model",
            "model": baseline_model,
            "strategy": "BALANCED",
            "teammate_map": None
        },
        {
            "name": "Advanced_Model",
            "model": advanced_model,
            "strategy": "BALANCED",
            "teammate_map": None
        },
        {
            "name": "Advanced_With_Teammate",
            "model": advanced_model,
            "strategy": "BALANCED",
            "teammate_map": teammate_map
        }
    ]

    for exp in experiments:
        print(f"\n=== RUNNING EXPERIMENT: {exp['name']} ===")

        decision_df = run_replay_validation(
            processed_laps_df=processed_laps_df,
            degradation_df=degradation_df,
            model=exp["model"],
            driver_id=driver_id,
            total_laps_allowed=total_laps_allowed,
            lap_distance_km=lap_distance_km,
            teammate_map=exp["teammate_map"]
        )

        metrics_df = compute_pit_metrics(decision_df)

        log_decisions(
            decision_df=decision_df,
            year=year,
            gp_name=gp_name,
            driver_id=driver_id,
            tag=exp["name"]
        )

        metrics_df["Experiment"] = exp["name"]
        experiment_results.append(metrics_df)

    final_results = pd.concat(experiment_results, ignore_index=True)

    print("\n=== EXPERIMENT SUMMARY ===")
    print(final_results)

    return final_results
