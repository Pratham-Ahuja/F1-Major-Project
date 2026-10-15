import streamlit as st
import plotly.graph_objects as go
import pandas as pd


# =========================================================
# STRATEGY COMPARISON PANEL
# =========================================================

def render_strategy_comparison(research_data: dict | None):
    """
    Compare multiple pit strategies and visualize heatmap.

    Parameters
    ----------
    research_data : dict
        Expected keys:
        - strategy_results
    """

    st.subheader("📉 Strategy Comparison")

    if research_data is None:
        st.warning("Research data not available")
        return

    strategies = research_data.get("strategy_results")

    if strategies is None or len(strategies) == 0:
        st.warning("Strategy comparison data missing")
        return

    pit_laps = []
    race_times = []
    risks = []

    for s in strategies:
        pit_laps.append(s.get("pit_lap"))
        race_times.append(s.get("mean_time"))
        risks.append(s.get("risk"))

    # -----------------------------------------------------
    # LINE CHART
    # -----------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=pit_laps,
            y=race_times,
            mode="lines+markers",
            marker=dict(size=10),
            line=dict(width=3),
            name="Expected Race Time",
            hovertemplate="Pit Lap %{x}<br>Race Time %{y:.2f}s<extra></extra>"
        )
    )

    fig.update_layout(
        title="Pit Strategy vs Expected Race Time",
        xaxis_title="Pit Lap",
        yaxis_title="Expected Race Time (s)",
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # HEATMAP
    # -----------------------------------------------------

    st.subheader("🔥 Strategy Heatmap")

    df = pd.DataFrame({
        "Pit Lap": pit_laps,
        "Expected Time": race_times
    })

    heatmap_fig = go.Figure(
        data=go.Heatmap(
            x=df["Pit Lap"],
            y=["Strategy Outcome"],
            z=[df["Expected Time"]],
            colorscale="Viridis",
            hovertemplate="Pit Lap %{x}<br>Expected Time %{z:.2f}s<extra></extra>"
        )
    )

    heatmap_fig.update_layout(
        xaxis_title="Pit Lap",
        yaxis_title="",
        height=250
    )

    st.plotly_chart(heatmap_fig, use_container_width=True)

    # -----------------------------------------------------
    # BEST STRATEGY
    # -----------------------------------------------------

    best_index = race_times.index(min(race_times))

    st.success(
        f"Best strategy: Pit on lap {pit_laps[best_index]}"
    )