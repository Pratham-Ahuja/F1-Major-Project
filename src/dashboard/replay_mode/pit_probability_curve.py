import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# =========================================================
# PIT PROBABILITY CURVE
# =========================================================

def render_pit_probability_curve(replay_data: dict | None):
    """
    Render pit probability curve across laps.

    Parameters
    ----------
    replay_data : dict
        Expected keys:
        - laps
        - pit_probabilities
    """

    st.subheader("📈 Pit Probability Curve")

    if replay_data is None:
        st.warning("Replay data not available")
        return

    laps = replay_data.get("laps")
    probs = replay_data.get("pit_probabilities")

    if laps is None or probs is None:
        st.warning("Pit probability data missing")
        return

    df = pd.DataFrame({
        "lap": laps,
        "probability": probs
    })

    if df.empty:
        st.warning("No pit probability samples found")
        return

    # -----------------------------------------------------
    # Plot curve
    # -----------------------------------------------------
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["lap"],
            y=df["probability"],
            mode="lines+markers",
            line=dict(width=3, color="#3498db"),
            marker=dict(size=6),
            name="Pit Probability",
            hovertemplate="Lap %{x}<br>Probability %{y:.2f}<extra></extra>"
        )
    )

    fig.update_layout(
        title="AI Pit Probability Across Laps",
        xaxis_title="Lap",
        yaxis_title="Pit Probability",
        yaxis=dict(range=[0, 1]),
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)