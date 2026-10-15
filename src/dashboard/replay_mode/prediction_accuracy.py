import streamlit as st
import plotly.graph_objects as go


# =========================================================
# PIT TIMING EVALUATION PANEL
# =========================================================

def render_prediction_accuracy(replay_data: dict | None):
    """
    Render AI pit timing evaluation for a single race.

    Parameters
    ----------
    replay_data : dict
        Expected keys:
        - ai_pit_lap
        - real_pit_lap
        - ai_pit_start
        - ai_pit_end
    """

    st.subheader("🎯 Pit Timing Evaluation")

    if replay_data is None:
        st.warning("Replay data not available")
        return

    ai_lap = replay_data.get("ai_pit_lap")
    real_lap = replay_data.get("real_pit_lap")
    window_start = replay_data.get("ai_pit_start")
    window_end = replay_data.get("ai_pit_end")

    if ai_lap is None or real_lap is None:
        st.warning("Pit timing data missing")
        return

    # -----------------------------------------------------
    # METRICS CALCULATION
    # -----------------------------------------------------

    delta = ai_lap - real_lap

    # Window Hit / Miss
    if window_start is not None and window_end is not None:
        hit = window_start <= real_lap <= window_end
    else:
        hit = False

    window_result = "HIT" if hit else "MISS"

    # Timing Score (0 to 1)
    tolerance = 10  # laps tolerance window
    score = max(0, 1 - abs(delta) / tolerance)

    # -----------------------------------------------------
    # DISPLAY METRICS
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric("AI Pit Lap", ai_lap)
    col2.metric("Real Pit Lap", real_lap)
    col3.metric("Lap Error", f"{delta} laps")

    st.divider()

    col4, col5 = st.columns(2)

    col4.metric("Window Result", window_result)
    col5.metric("Timing Score", f"{score:.2f}")

    # -----------------------------------------------------
    # VISUALIZATION (Delta Bar)
    # -----------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=["AI Pit", "Real Pit"],
            y=[ai_lap, real_lap],
            marker_color=["#3498db", "#e74c3c"]
        )
    )

    fig.update_layout(
        title="AI vs Real Pit Lap Comparison",
        yaxis_title="Lap Number",
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # INTERPRETATION
    # -----------------------------------------------------

    if delta < 0:
        st.info("AI predicted the pit stop earlier than the actual stop.")
    elif delta > 0:
        st.info("AI predicted the pit stop later than the actual stop.")
    else:
        st.success("AI predicted the pit stop exactly.")

    if hit:
        st.success("Real pit occurred within AI predicted window.")
    else:
        st.warning("Real pit occurred outside AI predicted window.")