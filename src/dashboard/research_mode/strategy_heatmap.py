import streamlit as st
import plotly.express as px
import pandas as pd


# =========================================================
# STRATEGY HEATMAP
# =========================================================

def render_strategy_heatmap(research_data: dict | None):

    st.subheader("🔥 Strategy Heatmap (Pit Lap vs Race Time)")

    if research_data is None:
        st.warning("Research data not available")
        return

    strategy_results = research_data.get("strategy_results")

    if strategy_results is None or len(strategy_results) == 0:
        st.warning("Strategy experiment data missing")
        return

    df = pd.DataFrame(strategy_results)

    fig = px.scatter(
        df,
        x="pit_lap",
        y="mean_time",
        color="risk",
        size="risk",
        color_continuous_scale="Turbo",
        labels={
            "pit_lap": "Pit Lap",
            "mean_time": "Expected Race Time",
            "risk": "Strategy Risk"
        },
        title="Pit Strategy Performance Landscape"
    )

    fig.update_layout(height=400)

    st.plotly_chart(fig, use_container_width=True)