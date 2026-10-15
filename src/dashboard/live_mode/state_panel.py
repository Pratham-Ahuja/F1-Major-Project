import streamlit as st


# =========================================================
# STATE PANEL — Live Race State Visualization
# =========================================================

def render_state_panel(race_state):
    """
    Render the live race state panel.

    Parameters
    ----------
    race_state : RaceState
        Current race state object from Phase 4
    """

    st.subheader("📊 Live Race State")

    if race_state is None:
        st.warning("Race state not available")
        return

    # =====================================================
    # BASIC RACE INFO
    # =====================================================
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Current Lap",
            value=race_state.current_lap
        )

    with col2:
        st.metric(
            label="Distance Covered (km)",
            value=f"{race_state.distance_covered_km:.2f}"
        )

    st.divider()

    # =====================================================
    # DRIVER STATUS
    # =====================================================
    st.markdown("### 👤 Driver Status")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Position", f"P{race_state.driver_position}")
        st.metric("Tyre Compound", race_state.driver_tyre)

    with col2:
        st.metric("Tyre Life (laps)", race_state.driver_tyre_life)
        st.metric("Current Stint", race_state.driver_stint)

    st.divider()

    # =====================================================
    # TEAMMATE CONTEXT
    # =====================================================
    if race_state.teammate_id is not None:

        st.markdown("### 🧑‍🤝‍🧑 Teammate Context")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Teammate", race_state.teammate_id)

        with col2:
            st.metric(
                "Teammate Position",
                f"P{race_state.teammate_position}"
            )

        st.divider()

    # =====================================================
    # WEATHER SNAPSHOT
    # =====================================================
    if race_state.weather_snapshot:

        st.markdown("### 🌦️ Weather Conditions")

        weather = race_state.weather_snapshot

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Track Temp (°C)", weather.get("TrackTemp", "-"))

        with col2:
            st.metric("Air Temp (°C)", weather.get("AirTemp", "-"))

        with col3:
            st.metric("Rainfall", weather.get("Rainfall", "-"))