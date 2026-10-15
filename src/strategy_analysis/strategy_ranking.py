from typing import List, Dict, Any


# =========================================================
# STRATEGY RANKING ENGINE
# =========================================================

def rank_strategies(strategy_summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank strategies based on expected race time and risk.

    Parameters
    ----------
    strategy_summaries : list of dict
        Output from strategy_comparison module.

    Each dict contains:
        - name
        - expected_time
        - risk

    Returns
    -------
    Ranked list of strategies (best → worst)
    """

    if not strategy_summaries:
        return []

    # Filter strategies that have valid expected time
    valid_strategies = [
        s for s in strategy_summaries
        if s.get("expected_time") is not None
    ]

    # Sort by expected_time first, then by risk
    ranked = sorted(
        valid_strategies,
        key=lambda s: (s["expected_time"], s.get("risk", float("inf")))
    )

    # Add ranking number
    for idx, strategy in enumerate(ranked, start=1):
        strategy["rank"] = idx

    return ranked