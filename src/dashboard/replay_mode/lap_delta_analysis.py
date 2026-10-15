import streamlit as st
import plotly.graph_objects as go


# =========================================================
# LAP DELTA ANALYSIS
# =========================================================

def render_lap_delta_analysis(replay_data: dict | None):
    """
    Render lap difference between AI predicted pit lap and real pit lap.

    Parameters
    ----------
    replay_data : dict
        Expected keys:
        - ai_pit_lap
        - real_pit_lap
    """

    st.subheader("📊 Lap Delta Analysis")

    if replay_data is None:
        st.warning("Replay data not available")
        return

    ai_lap = replay_data.get("ai_pit_lap")
    real_lap = replay_data.get("real_pit_lap")

    if ai_lap is None or real_lap is None:
        st.warning("Pit lap comparison data missing")
        return

    delta = ai_lap - real_lap

    # -----------------------------------------------------
    # Bar chart visualization
    # -----------------------------------------------------
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=["AI Pit Lap", "Real Pit Lap"],
            y=[ai_lap, real_lap],
            marker_color=["#3498db", "#e74c3c"]
        )
    )

    fig.update_layout(
        title="AI vs Real Pit Lap",
        yaxis_title="Lap Number",
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # Delta Metric
    # -----------------------------------------------------
    st.metric(
        label="Lap Difference (AI − Real)",
        value=f"{delta} laps"
    )

    # -----------------------------------------------------
    # Interpretation
    # -----------------------------------------------------
    if delta < 0:
        st.info("AI predicted the pit stop earlier than the actual stop.")
    elif delta > 0:
        st.info("AI predicted the pit stop later than the actual stop.")
    else:
        st.success("AI predicted the pit stop exactly.")