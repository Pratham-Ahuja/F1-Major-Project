import streamlit as st
import plotly.graph_objects as go
import numpy as np
import fastf1


# =========================================================
# CIRCUIT MAP PANEL — Track Layout & Driver Positions
# =========================================================

def _load_fastf1_track(season, gp):
    """
    Load circuit coordinates from FastF1 telemetry.
    """

    try:

        session = fastf1.get_session(season, gp, "R")
        session.load(laps=False, telemetry=True)

        lap = session.laps.pick_fastest()
        telemetry = lap.get_telemetry()

        x = telemetry["X"].values
        y = telemetry["Y"].values

        return {"x": x, "y": y}

    except Exception as e:

        print("FastF1 track load failed:", e)

        return None


def render_circuit_map(
    circuit_coords: dict | None,
    driver_progress: float | None = None,
    teammate_progress: float | None = None,
    all_drivers: list | None = None,
    season: int | None = None,
    gp: str | None = None
):

    """
    Render circuit map with driver positions.
    """

    st.subheader("🗺️ Circuit Map & Live Driver Positions")

    # -----------------------------------------------------
    # LOAD CIRCUIT GEOMETRY
    # -----------------------------------------------------

    if circuit_coords is None and season and gp:
        circuit_coords = _load_fastf1_track(season, gp)

    # -----------------------------------------------------
    # FALLBACK OVAL
    # -----------------------------------------------------

    if circuit_coords is None:

        t = np.linspace(0, 2 * np.pi, 800)
        x = np.cos(t)
        y = np.sin(t)

    else:

        x = circuit_coords.get("x", [])
        y = circuit_coords.get("y", [])

    if len(x) < 10 or len(y) < 10:
        st.warning("Circuit geometry not available")
        return

    fig = go.Figure()

    # -----------------------------------------------------
    # TRACK LAYOUT
    # -----------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(width=4, color="#444"),
            name="Track",
            hoverinfo="skip"
        )
    )

    # -----------------------------------------------------
    # GENERATE RANDOM DRIVERS IF NONE PROVIDED
    # -----------------------------------------------------

    if all_drivers is None:

        all_drivers = []

        for i in range(20):

            all_drivers.append(
                {
                    "name": f"DRV{i+1}",
                    "progress": np.random.random(),
                    "position": i + 1
                }
            )

    # -----------------------------------------------------
    # ALL DRIVERS
    # -----------------------------------------------------

    driver_x = []
    driver_y = []
    labels = []
    hover_text = []

    for d in all_drivers:

        progress = d.get("progress", 0)

        idx = int(progress * (len(x) - 1))

        driver_x.append(x[idx])
        driver_y.append(y[idx])

        label = d.get("name", "DRV")
        position = d.get("position", "?")

        labels.append(label)

        hover_text.append(
            f"Driver: {label}<br>"
            f"Position: P{position}<br>"
            f"Lap Progress: {round(progress*100,1)}%"
        )

    fig.add_trace(
        go.Scatter(
            x=driver_x,
            y=driver_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            marker=dict(
                size=10,
                color="#3498db",
                line=dict(width=1, color="white")
            ),
            name="Drivers",
            hovertext=hover_text,
            hoverinfo="text"
        )
    )

    # -----------------------------------------------------
    # SELECTED DRIVER (Highlighted)
    # -----------------------------------------------------

    if driver_progress is not None:

        idx = int(driver_progress * (len(x) - 1))

        fig.add_trace(
            go.Scatter(
                x=[x[idx]],
                y=[y[idx]],
                mode="markers+text",
                text=["YOU"],
                textposition="bottom center",
                marker=dict(
                    size=16,
                    color="red",
                    line=dict(width=2, color="white")
                ),
                name="Selected Driver",
                hovertext=f"Selected Driver<br>Progress: {round(driver_progress*100,1)}%",
                hoverinfo="text"
            )
        )

    # -----------------------------------------------------
    # TEAMMATE
    # -----------------------------------------------------

    if teammate_progress is not None:

        idx = int(teammate_progress * (len(x) - 1))

        fig.add_trace(
            go.Scatter(
                x=[x[idx]],
                y=[y[idx]],
                mode="markers+text",
                text=["TM"],
                textposition="bottom center",
                marker=dict(
                    size=13,
                    color="#2ecc71",
                    line=dict(width=1, color="white")
                ),
                name="Teammate",
                hovertext=f"Teammate<br>Progress: {round(teammate_progress*100,1)}%",
                hoverinfo="text"
            )
        )

    # -----------------------------------------------------
    # Layout Styling
    # -----------------------------------------------------

    fig.update_layout(
        title="Live Circuit Position Map",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=450,
        showlegend=True,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Driver positions are estimated using lap progress along the circuit path."
    )