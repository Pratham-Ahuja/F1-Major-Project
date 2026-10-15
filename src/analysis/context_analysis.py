"""
Phase 5 — Context & Analysis Orchestrator

This module aggregates:
- Tyre degradation analysis (5.1)
- Rolling pace analysis (5.2)
- Traffic & gap analysis (5.3)

It acts as a SINGLE ENTRY POINT for Phase 6 (Feature Engineering)
and later phases.

NO ML.
NO DECISIONS.
NO SIMULATIONS.
"""

from typing import Dict

import pandas as pd

from src.analysis.tyre_degradation import tyre_degradation_analysis
from src.analysis.pace_analysis import rolling_pace_analysis
from src.analysis.traffic_analysis import traffic_gap_analysis


# =========================================================
# PHASE 5 — CONTEXT AGGREGATION
# =========================================================

def run_context_analysis(
    processed_laps_df: pd.DataFrame
) -> Dict[str, object]:
    """
    Run full context analysis pipeline.

    Parameters
    ----------
    processed_laps_df : pd.DataFrame
        Output of Phase 3 (processed lap-level data)

    Returns
    -------
    context : Dict[str, object]
        {
            "tyre": {
                "stint_degradation": DataFrame,
                "compound_summary": DataFrame
            },
            "pace": {
                "laps_with_pace": DataFrame
            },
            "traffic": {
                "laps_with_gaps": DataFrame,
                "driver_summary": DataFrame
            }
        }
    """

    # -----------------------------------------------------
    # STEP 5.1 — Tyre degradation analysis
    # -----------------------------------------------------
    stint_degradation_df, compound_summary_df = (
        tyre_degradation_analysis(processed_laps_df)
    )

    # -----------------------------------------------------
    # STEP 5.2 — Rolling pace analysis
    # -----------------------------------------------------
    laps_with_pace_df = rolling_pace_analysis(processed_laps_df)

    # -----------------------------------------------------
    # STEP 5.3 — Traffic & gap analysis
    # -----------------------------------------------------
    laps_with_gaps_df, traffic_summary_df = (
        traffic_gap_analysis(processed_laps_df)
    )

    # -----------------------------------------------------
    # Aggregate context
    # -----------------------------------------------------
    context = {
        "tyre": {
            "stint_degradation": stint_degradation_df,
            "compound_summary": compound_summary_df
        },
        "pace": {
            "laps_with_pace": laps_with_pace_df
        },
        "traffic": {
            "laps_with_gaps": laps_with_gaps_df,
            "driver_summary": traffic_summary_df
        }
    }

    return context
