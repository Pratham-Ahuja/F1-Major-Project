import streamlit as st
import plotly.graph_objects as go


# =========================================================
# STRATEGY TIMELINE
# =========================================================

def render_strategy_timeline(research_data: dict | None):
    """
    Render AI strategy timeline.

    Parameters
    ----------
    research_data : dict
        Expected keys:
        - pit_laps (list)
        - compounds (list)
        - laps (list)
    """

    st.subheader("🕒 Strategy Timeline")

    if research_data is None:
        st.warning("Research data not available")
        return

    pit_laps = research_data.get("pit_laps", [])
    compounds = research_data.get("compounds", [])
    laps = research_data.get("laps", [])

    if not pit_laps or not compounds or not laps:
        st.warning("Strategy timeline data missing")
        return

    # -----------------------------------------------------
    # Map compounds to pit laps
    # -----------------------------------------------------

    pit_compounds = []

    for lap in pit_laps:

        try:
            index = laps.index(lap)
            pit_compounds.append(compounds[index])
        except:
            pit_compounds.append("Unknown")

    # -----------------------------------------------------
    # Plot Strategy Events
    # -----------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=pit_laps,
            y=["Pit Stop"] * len(pit_laps),
            mode="markers+text",
            marker=dict(size=14, color="#e67e22"),
            text=pit_compounds,
            textposition="top center",
            hovertemplate="Lap %{x}<br>Compound %{text}<extra></extra>"
        )
    )

    fig.update_layout(
        title="AI Strategy Events",
        xaxis_title="Lap",
        yaxis=dict(showticklabels=False),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)