import streamlit as st
import plotly.graph_objects as go


# =========================================================
# TYRE STINT VISUALIZATION
# =========================================================

def render_tyre_stints(research_data: dict | None):

    st.subheader("🛞 Tyre Stint Strategy")

    if research_data is None:
        st.warning("Research data not available")
        return

    pit_laps = research_data.get("pit_laps", [])
    compounds = research_data.get("compounds", [])
    total_laps = research_data.get("total_laps")

    if total_laps is None:
        st.warning("Total lap data missing")
        return

    # -----------------------------------------------------
    # CLEAN PIT LAPS
    # -----------------------------------------------------

    pit_laps = sorted(list(set([int(p) for p in pit_laps if p is not None])))

    # -----------------------------------------------------
    # DETERMINE STARTING COMPOUND
    # -----------------------------------------------------

    if compounds and compounds[0] is not None:
        start_compound = str(compounds[0]).upper()
    else:
        start_compound = "MEDIUM"

    # -----------------------------------------------------
    # COMPOUND ROTATION
    # -----------------------------------------------------

    compound_order = ["SOFT", "MEDIUM", "HARD"]

    if start_compound not in compound_order:
        start_compound = "MEDIUM"

    current_index = compound_order.index(start_compound)

    # -----------------------------------------------------
    # BUILD STINT STRUCTURE
    # -----------------------------------------------------

    stints = []

    current_compound = start_compound
    start_lap = 1

    for pit in pit_laps:

        stints.append({
            "compound": current_compound,
            "start_lap": start_lap,
            "end_lap": pit
        })

        # rotate compound after pit
        current_index = (current_index + 1) % len(compound_order)
        current_compound = compound_order[current_index]

        start_lap = pit + 1

    # final stint
    if start_lap <= total_laps:
        stints.append({
            "compound": current_compound,
            "start_lap": start_lap,
            "end_lap": total_laps
        })

    # -----------------------------------------------------
    # COLOR MAP
    # -----------------------------------------------------

    colors = {
        "SOFT": "#e74c3c",
        "MEDIUM": "#f1c40f",
        "HARD": "#ecf0f1"
    }

    # -----------------------------------------------------
    # PLOT
    # -----------------------------------------------------

    fig = go.Figure()

    for stint in stints:

        compound = stint["compound"]
        start = stint["start_lap"]
        end = stint["end_lap"]

        stint_length = end - start + 1

        fig.add_trace(
            go.Bar(
                x=[stint_length],
                y=["Strategy"],
                base=[start],
                orientation="h",
                marker=dict(color=colors.get(compound, "#3498db")),
                hovertemplate=f"{compound}<br>Lap {start} → {end}<extra></extra>",
                showlegend=False
            )
        )

    fig.update_layout(
        title="Tyre Stint Timeline",
        xaxis_title="Lap",
        yaxis=dict(showticklabels=False),
        height=300,
        barmode="overlay"
    )

    st.plotly_chart(fig, use_container_width=True)