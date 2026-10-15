from typing import Dict, Any
from src.state.race_state import RaceState


# =========================================================
# DATA ADAPTER — Core Objects → Dashboard-Friendly Data
# =========================================================

# ---------------------------------------------------------
# LIVE MODE ADAPTER
# ---------------------------------------------------------

def adapt_race_state(race_state: RaceState) -> Dict[str, Any]:
    """
    Convert RaceState object into a dashboard-friendly dictionary.
    """

    if race_state is None:
        return {}

    return {
        "current_lap": getattr(race_state, "current_lap", None),
        "distance_covered_km": getattr(race_state, "distance_covered_km", None),

        "driver_id": getattr(race_state, "driver_id", None),
        "driver_position": getattr(race_state, "driver_position", None),
        "driver_tyre": getattr(race_state, "driver_tyre", None),
        "driver_tyre_life": getattr(race_state, "driver_tyre_life", None),
        "driver_stint": getattr(race_state, "driver_stint", None),

        "teammate_id": getattr(race_state, "teammate_id", None),
        "teammate_position": getattr(race_state, "teammate_position", None),

        "weather": getattr(race_state, "weather_snapshot", None),

        "history": getattr(race_state, "history", [])
    }


# ---------------------------------------------------------
# DECISION ADAPTER
# ---------------------------------------------------------

def adapt_decision(decision) -> Dict[str, Any]:
    """
    Convert DecisionResult object into dashboard-friendly format.
    """

    if decision is None:
        return {}

    return {
        "action": getattr(decision, "action", None),
        "confidence": getattr(decision, "confidence", None),
        "risk_level": getattr(decision, "risk_level", None),
        "strategy_type": getattr(decision, "strategy_type", None),
        "teammate_assist": getattr(decision, "teammate_assist", False),
        "explanation": getattr(decision, "explanation", "")
    }


# ---------------------------------------------------------
# MONTE CARLO ADAPTER
# ---------------------------------------------------------

def adapt_monte_carlo(mc_results) -> Dict[str, Any]:
    """
    Convert Monte Carlo simulation output into dashboard-friendly format.
    """

    if mc_results is None:
        return {}

    return {
        "outcomes": mc_results.get("outcomes", []),
        "best_case": mc_results.get("best_case"),
        "expected_case": mc_results.get("expected_case"),
        "worst_case": mc_results.get("worst_case"),
        "risk_level": mc_results.get("risk_level")
    }


# =========================================================
# REPLAY MODE ADAPTER
# =========================================================

def adapt_replay_data(replay_results) -> Dict[str, Any]:
    """
    Convert replay evaluation results into dashboard-friendly format.
    """

    if replay_results is None:
        return {}

    return {

        # Pit probability curve
        "laps": replay_results.get("laps", []),
        "pit_probabilities": replay_results.get("pit_probabilities", []),

        # AI vs Real pit
        "ai_pit_start": replay_results.get("ai_pit_start"),
        "ai_pit_end": replay_results.get("ai_pit_end"),
        "real_pit_lap": replay_results.get("real_pit_lap"),

        # Lap delta
        "ai_pit_lap": replay_results.get("ai_pit_lap"),

        # Accuracy metrics
        "true_positive": replay_results.get("true_positive", 0),
        "false_positive": replay_results.get("false_positive", 0),
        "false_negative": replay_results.get("false_negative", 0),

        "accuracy": replay_results.get("accuracy", 0.0),
        "precision": replay_results.get("precision", 0.0),
        "recall": replay_results.get("recall", 0.0),
        "f1_score": replay_results.get("f1_score", 0.0),
    }


# =========================================================
# RESEARCH MODE ADAPTER
# =========================================================

def adapt_research_data(research_results) -> Dict[str, Any]:
    """
    Convert strategy research outputs into dashboard-friendly format.
    """

    if research_results is None:
        return {}

    return {

        # Strategy timeline
        "pit_laps": research_results.get("pit_laps", []),
        "compounds": research_results.get("compounds", []),

        # Tyre stints
        "stints": research_results.get("stints", []),

        # Position evolution
        "laps": research_results.get("laps", []),
        "positions": research_results.get("positions", []),

        # Strategy risk distribution
        "outcomes": research_results.get("outcomes", [])
    }