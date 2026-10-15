import streamlit as st

from src.dashboard.research_mode.evaluation_metrics import render_evaluation_metrics
from src.dashboard.research_mode.strategy_timeline import render_strategy_timeline
from src.dashboard.research_mode.tyre_stints import render_tyre_stints
from src.dashboard.research_mode.strategy_risk_distribution import render_strategy_risk_distribution
from src.dashboard.research_mode.strategy_comparison import render_strategy_comparison


# =========================================================
# RESEARCH MODE DASHBOARD LAYOUT
# =========================================================

def render_research_dashboard(research_data: dict | None):

    st.title("🧪 Research Mode — Strategy Exploration")

    st.divider()

    # -----------------------------------------------------
    # MODEL EVALUATION
    # -----------------------------------------------------

    render_evaluation_metrics(research_data)

    st.divider()

    # -----------------------------------------------------
    # ROW 1
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        render_strategy_timeline(research_data)

    with col2:
        render_tyre_stints(research_data)

    st.divider()

    # -----------------------------------------------------
    # ROW 2
    # -----------------------------------------------------

    col3, col4 = st.columns(2)

    with col3:
        render_strategy_comparison(research_data)

    with col4:
        render_strategy_risk_distribution(research_data)