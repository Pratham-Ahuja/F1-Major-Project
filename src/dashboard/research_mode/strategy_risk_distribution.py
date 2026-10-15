import streamlit as st
import plotly.graph_objects as go
import numpy as np


# =========================================================
# STRATEGY RISK DISTRIBUTION
# =========================================================

def render_strategy_risk_distribution(research_data: dict | None):
    """
    Render Monte Carlo distribution of strategy outcomes.

    Parameters
    ----------
    research_data : dict
        Expected keys:
        - outcomes (list of simulated race outcomes)
    """

    st.subheader("📊 Strategy Risk Distribution")

    if research_data is None:
        st.warning("Research data not available")
        return

    outcomes = research_data.get("outcomes")

    if outcomes is None or len(outcomes) == 0:
        st.warning("Strategy risk data missing")
        return

    outcomes = np.array(outcomes)

    mean_val = np.mean(outcomes)
    std_val = np.std(outcomes)

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=outcomes,
            nbinsx=30,
            marker_color="#9b59b6",
            opacity=0.75,
            name="Simulated Outcomes",
            hovertemplate="Outcome %{x:.2f}<br>Count %{y}<extra></extra>"
        )
    )

    # Mean line
    fig.add_vline(
        x=mean_val,
        line_color="black",
        line_width=2,
        annotation_text="Mean"
    )

    fig.update_layout(
        title="Strategy Outcome Distribution",
        xaxis_title="Race Outcome Metric",
        yaxis_title="Frequency",
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # Risk summary metrics
    # -----------------------------------------------------
    col1, col2 = st.columns(2)

    col1.metric("Mean Outcome", f"{mean_val:.2f}")
    col2.metric("Std Deviation", f"{std_val:.2f}")

    st.caption(
        "Distribution shows the uncertainty range of the strategy outcome "
        "based on Monte Carlo simulations."
    )