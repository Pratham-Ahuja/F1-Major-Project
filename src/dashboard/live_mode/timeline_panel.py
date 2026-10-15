import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# =========================================================
# TIMELINE PANEL — Strategy History (Lap-by-Lap)
# =========================================================

def render_timeline_panel(history: list | None):
    """
    Render strategy timeline panel.

    Parameters
    ----------
    history : list of dict
        Each dict is a snapshot logged in RaceState.history

        Expected keys:
        - lap
        - driver_position
        - driver_tyre
        - driver_tyre_life
        - decision (optional)
        - confidence (optional)
        - strategy_type (optional)
    """

    st.subheader("🕒 Strategy Timeline")

    if not history:
        st.warning("No race history available yet")
        return

    df = pd.DataFrame(history)

    if df.empty or "lap" not in df.columns:
        st.warning("Insufficient timeline data")
        return

    # -----------------------------------------------------
    # Ensure optional fields exist
    # -----------------------------------------------------
    for col in ["decision", "confidence", "strategy_type"]:
        if col not in df.columns:
            df[col] = None

    # -----------------------------------------------------
    # Expandable raw timeline table
    # -----------------------------------------------------
    with st.expander("📋 View Detailed Timeline Data"):
        st.dataframe(
            df.sort_values("lap"),
            use_container_width=True
        )

    # =====================================================
    # DRIVER POSITION EVOLUTION
    # =====================================================

    if "driver_position" in df.columns:

        fig_pos = go.Figure()

        fig_pos.add_trace(
            go.Scatter(
                x=df["lap"],
                y=df["driver_position"],
                mode="lines+markers",
                line=dict(width=3, color="#3498db"),
                marker=dict(size=6),
                name="Race Position",
                hovertemplate="Lap %{x}<br>Position P%{y}<extra></extra>"
            )
        )

        fig_pos.update_layout(
            title="Driver Position Evolution",
            xaxis_title="Lap",
            yaxis_title="Position",
            yaxis=dict(autorange="reversed"),  # P1 at top
            height=350
        )

        st.plotly_chart(fig_pos, use_container_width=True)

    # =====================================================
    # DECISION CONFIDENCE TIMELINE
    # =====================================================

    if df["confidence"].notna().any():

        fig_conf = go.Figure()

        fig_conf.add_trace(
            go.Scatter(
                x=df["lap"],
                y=df["confidence"],
                mode="lines+markers",
                name="Decision Confidence",
                line=dict(width=3, color="#2ecc71"),
                marker=dict(size=6),
                hovertemplate="Lap %{x}<br>Confidence %{y:.2f}<extra></extra>"
            )
        )

        fig_conf.update_layout(
            title="AI Decision Confidence Over Time",
            xaxis_title="Lap",
            yaxis_title="Confidence",
            yaxis=dict(range=[0, 1]),
            height=350
        )

        st.plotly_chart(fig_conf, use_container_width=True)

    # =====================================================
    # TYRE LIFE EVOLUTION
    # =====================================================

    if "driver_tyre_life" in df.columns:

        fig_tyre = go.Figure()

        fig_tyre.add_trace(
            go.Scatter(
                x=df["lap"],
                y=df["driver_tyre_life"],
                mode="lines+markers",
                name="Tyre Life",
                line=dict(width=3, color="#e67e22"),
                marker=dict(size=6),
                hovertemplate="Lap %{x}<br>Tyre Life %{y}<extra></extra>"
            )
        )

        fig_tyre.update_layout(
            title="Tyre Life Progression",
            xaxis_title="Lap",
            yaxis_title="Tyre Life (laps)",
            height=350
        )

        st.plotly_chart(fig_tyre, use_container_width=True)

    # =====================================================
    # STRATEGY TYPE DISTRIBUTION
    # =====================================================

    if df["strategy_type"].notna().any():

        strategy_counts = df["strategy_type"].value_counts()

        fig_strategy = go.Figure(
            data=[
                go.Bar(
                    x=strategy_counts.index,
                    y=strategy_counts.values,
                    marker_color="#9b59b6"
                )
            ]
        )

        fig_strategy.update_layout(
            title="Strategy Mode Usage",
            xaxis_title="Strategy Mode",
            yaxis_title="Number of Laps",
            height=350
        )

        st.plotly_chart(fig_strategy, use_container_width=True)