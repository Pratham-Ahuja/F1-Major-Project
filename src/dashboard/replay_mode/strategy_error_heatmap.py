import streamlit as st
import plotly.graph_objects as go
import numpy as np


# =========================================================
# STRATEGY ERROR HEATMAP
# =========================================================

def render_strategy_error_heatmap(replay_data: dict | None):
    """
    Visualize AI prediction error across race laps.
    """

    st.subheader("🔥 Strategy Error Heatmap")

    if replay_data is None:
        st.warning("Replay data not available")
        return

    laps = replay_data.get("laps")
    ai_lap = replay_data.get("ai_pit_lap")
    real_lap = replay_data.get("real_pit_lap")

    if laps is None or ai_lap is None or real_lap is None:
        st.warning("Heatmap data missing")
        return

    # -----------------------------------------------------
    # ERROR CALCULATION
    # -----------------------------------------------------

    errors = []

    for lap in laps:
        # error relative to real pit
        error = abs(lap - real_lap)

        # weight error around AI prediction
        distance_from_ai = abs(lap - ai_lap)

        # combined error score
        score = error + 0.5 * distance_from_ai

        errors.append(score)

    errors = np.array(errors)

    # normalize for visualization
    errors = (errors - errors.min()) / (errors.max() - errors.min() + 1e-6)

    heatmap = [errors]

    # -----------------------------------------------------
    # PLOT
    # -----------------------------------------------------

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap,
            x=laps,
            y=["Error Intensity"],
            colorscale="Reds",
            colorbar=dict(title="Error")
        )
    )

    fig.update_layout(
        title="AI Strategy Error Across Laps",
        xaxis_title="Lap",
        height=250
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # INTERPRETATION
    # -----------------------------------------------------

    st.caption("Darker regions indicate higher prediction error.")