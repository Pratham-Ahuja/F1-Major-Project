from typing import Dict, Any, List
import numpy as np


# =========================================================
# STRATEGY COMPARISON ENGINE
# =========================================================

def compare_strategies(strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compare multiple strategies using simulation outcomes.

    Parameters
    ----------
    strategies : list of dict

    Each strategy dict should contain:
    - name
    - pit_laps
    - compounds
    - outcomes (Monte Carlo results)

    Returns
    -------
    List of strategy summaries
    """

    results = []

    if not strategies:
        return results

    for strategy in strategies:

        outcomes = strategy.get("outcomes", [])

        if not outcomes:
            mean_time = None
            risk = None
        else:
            mean_time = float(np.mean(outcomes))
            risk = float(np.std(outcomes))

        summary = {
            "name": strategy.get("name"),
            "pit_laps": strategy.get("pit_laps", []),
            "compounds": strategy.get("compounds", []),
            "expected_time": mean_time,
            "risk": risk
        }

        results.append(summary)

    return results