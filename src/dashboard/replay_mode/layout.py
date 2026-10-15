import streamlit as st

from src.dashboard.replay_mode.pit_probability_curve import render_pit_probability_curve
from src.dashboard.replay_mode.ai_vs_real_pit import render_ai_vs_real_pit
from src.dashboard.replay_mode.prediction_accuracy import render_prediction_accuracy
from src.dashboard.replay_mode.lap_delta_analysis import render_lap_delta_analysis
from src.dashboard.replay_mode.strategy_error_heatmap import render_strategy_error_heatmap
from src.dashboard.replay_mode.tyre_degradation_curve import render_tyre_degradation_curve


# =========================================================
# REPLAY MODE DASHBOARD LAYOUT
# =========================================================

def render_replay_dashboard(replay_data):
    """
    Render Replay Mode dashboard.

    Parameters
    ----------
    replay_data : dict
        Contains evaluation data for AI vs real strategy.
    """

    st.title("🔁 Replay Mode — Strategy Evaluation")

    st.divider()

    # -------------------------------------------
    # Row 1
    # -------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        render_pit_probability_curve(replay_data)

    with col2:
        render_ai_vs_real_pit(replay_data)

    st.divider()

    # -------------------------------------------
    # Row 2
    # -------------------------------------------
    col3, col4 = st.columns(2)

    with col3:
        render_prediction_accuracy(replay_data)

    with col4:
        render_lap_delta_analysis(replay_data)

    st.divider()

    # -------------------------------------------
    # Row 3 (FINAL)
    # -------------------------------------------
    col5, col6 = st.columns(2)

    with col5:
        render_strategy_error_heatmap(replay_data)

    with col6:
        render_tyre_degradation_curve(replay_data)