import streamlit as st
import plotly.graph_objects as go


# =========================================================
# AI VS REAL PIT TIMELINE
# =========================================================

def render_ai_vs_real_pit(replay_data: dict | None):
    """
    Render comparison between AI pit window and real pit stop.

    Parameters
    ----------
    replay_data : dict
        Expected keys:
        - ai_pit_start
        - ai_pit_end
        - real_pit_lap
    """

    st.subheader("⏱ AI vs Real Pit Timing")

    if replay_data is None:
        st.warning("Replay data not available")
        return

    ai_start = replay_data.get("ai_pit_start")
    ai_end = replay_data.get("ai_pit_end")
    real_pit = replay_data.get("real_pit_lap")

    if ai_start is None or ai_end is None or real_pit is None:
        st.warning("Pit timing data missing")
        return

    fig = go.Figure()

    # -----------------------------------------------------
    # AI pit window
    # -----------------------------------------------------
    fig.add_trace(
        go.Bar(
            x=[ai_end - ai_start],
            y=["AI Pit Window"],
            base=[ai_start],
            orientation="h",
            marker=dict(color="#3498db"),
            name="AI Pit Window"
        )
    )

    # -----------------------------------------------------
    # Real pit stop marker
    # -----------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=[real_pit],
            y=["Real Pit Stop"],
            mode="markers",
            marker=dict(size=14, color="red"),
            name="Real Pit Lap",
            hovertemplate="Real Pit Lap: %{x}<extra></extra>"
        )
    )

    fig.update_layout(
        title="AI Pit Window vs Actual Pit Stop",
        xaxis_title="Lap",
        height=300,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)