import streamlit as st
import plotly.graph_objects as go
import numpy as np


# =========================================================
# TYRE DEGRADATION VS PIT PROBABILITY
# =========================================================

def render_tyre_degradation_curve(replay_data: dict | None):
    """
    Show relationship between tyre life and pit probability.
    """

    st.subheader("🛞 Tyre Degradation vs Pit Probability")

    if replay_data is None:
        st.warning("Replay data not available")
        return

    laps = replay_data.get("laps")
    pit_probs = replay_data.get("pit_probabilities")
    real_pit_lap = replay_data.get("real_pit_lap")

    if laps is None or pit_probs is None:
        st.warning("Tyre degradation data missing")
        return

    # -----------------------------------------------------
    # REALISTIC TYRE LIFE (RESET ON PIT)
    # -----------------------------------------------------

    tyre_life = []
    current_life = 0

    for lap in laps:

        # Reset tyre life at pit stop
        if real_pit_lap is not None and lap == real_pit_lap:
            current_life = 0

        tyre_life.append(current_life)
        current_life += 1

    tyre_life = np.array(tyre_life)

    # Normalize safely
    tyre_life_norm = tyre_life / (tyre_life.max() + 1e-6)

    # -----------------------------------------------------
    # PLOT
    # -----------------------------------------------------

    fig = go.Figure()

    # Pit probability curve
    fig.add_trace(
        go.Scatter(
            x=laps,
            y=pit_probs,
            mode="lines",
            name="Pit Probability",
            line=dict(width=3)
        )
    )

    # Tyre degradation curve
    fig.add_trace(
        go.Scatter(
            x=laps,
            y=tyre_life_norm,
            mode="lines",
            name="Tyre Degradation",
            line=dict(width=2, dash="dash")
        )
    )

    fig.update_layout(
        title="Tyre Degradation vs Pit Probability",
        xaxis_title="Lap",
        yaxis_title="Normalized Value",
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # INTERPRETATION
    # -----------------------------------------------------

    if real_pit_lap:
        st.caption(
            f"Tyre degradation resets at lap {real_pit_lap} due to pit stop."
        )

    st.caption(
        "Ideally, pit probability should increase as tyre degradation increases."
    )