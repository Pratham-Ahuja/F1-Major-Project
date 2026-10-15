from typing import Dict, Any
import numpy as np


# =========================================================
# STRATEGY REPORT GENERATOR
# =========================================================

def generate_strategy_report(strategy_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary report for AI strategy.

    Parameters
    ----------
    strategy_data : dict

    Expected keys:
    - pit_laps
    - compounds
    - outcomes (Monte Carlo results)
    """

    if strategy_data is None:
        return {}

    pit_laps = strategy_data.get("pit_laps", [])
    compounds = strategy_data.get("compounds", [])
    outcomes = strategy_data.get("outcomes", [])

    stops = len(pit_laps)

    if stops > 0:
        stint_lengths = np.diff([0] + pit_laps)
        avg_stint = float(np.mean(stint_lengths))
    else:
        avg_stint = None

    if outcomes:
        mean_time = float(np.mean(outcomes))
        risk = float(np.std(outcomes))
    else:
        mean_time = None
        risk = None

    report = {
        "total_stops": stops,
        "pit_laps": pit_laps,
        "compounds": compounds,
        "average_stint_length": avg_stint,
        "expected_race_time": mean_time,
        "risk_spread": risk
    }

    return report