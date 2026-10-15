# =========================================================
# MODE CONTROLLER
# =========================================================

import streamlit as st

# =========================================================
# DASHBOARD IMPORTS
# =========================================================

# Live dashboard
from src.dashboard.app import main as live_dashboard

# Replay dashboard
from src.dashboard.replay_mode.layout import render_replay_dashboard

# Research dashboard
from src.dashboard.research_mode.layout import render_research_dashboard


# =========================================================
# MODE LAUNCHER
# =========================================================

def launch_mode(mode, race_loop):
    """
    Launch correct system mode.
    race_loop is provided by PipelineController
    """

    # -----------------------------------------------------
    # LIVE MODE
    # -----------------------------------------------------

    if mode == "Live Strategy":

        st.success("Live Strategy Mode Activated")

        # -------------------------------------------------
        # Initialize race loop once
        # -------------------------------------------------

        if "race_loop" not in st.session_state:
            st.session_state["race_loop"] = race_loop

        if "race_generator" not in st.session_state:
            st.session_state["race_generator"] = race_loop.run()

        gen = st.session_state.get("race_generator")

        if gen is None:
            st.error("Race generator not initialized.")
            return

        # -------------------------------------------------
        # Advance one lap safely
        # -------------------------------------------------

        try:

            state = next(gen)

            # Store state for dashboard
            st.session_state["race_state"] = state

        except StopIteration:

            st.success("Race Simulation Completed")

            # Reset generator
            st.session_state["race_generator"] = None

            return

        except ValueError:

            # Fix for "generator already executing"
            st.warning("Race loop already running. Waiting for next refresh.")
            return

        # -------------------------------------------------
        # Render live dashboard
        # -------------------------------------------------

        live_dashboard()

        return


    # -----------------------------------------------------
    # REPLAY MODE
    # -----------------------------------------------------

    elif mode == "Replay Analysis":

        st.success("Replay Analysis Mode")

        replay_data = race_loop

        st.session_state["analysis_data"] = replay_data

        render_replay_dashboard(replay_data)

        return


    # -----------------------------------------------------
    # RESEARCH MODE
    # -----------------------------------------------------

    elif mode == "Research Simulation":

        st.success("Research Simulation Mode")

        research_data = race_loop

        st.session_state["analysis_data"] = research_data

        render_research_dashboard(research_data)

        return