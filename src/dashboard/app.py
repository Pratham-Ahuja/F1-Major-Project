import sys
import os

# =========================================================
# FIX PYTHON PATH FOR 'src' IMPORTS
# =========================================================
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )
)

import streamlit as st
import fastf1
import datetime
import numpy as np

# =========================================================
# PIPELINE
# =========================================================
from src.system.pipeline_controller import PipelineController

# =========================================================
# RESEARCH MODE
# =========================================================
from src.dashboard.research_mode.layout import render_research_dashboard
from src.monte_carlo.monte_carlo_simulator import MonteCarloSimulator
from src.simulation.strategy_simulator import SimulationResult

# =========================================================
# LIVE MODE
# =========================================================
from src.dashboard.live_mode.state_panel import render_state_panel
from src.dashboard.live_mode.decision_panel import render_decision_panel
from src.dashboard.live_mode.risk_panel import render_risk_panel
from src.dashboard.live_mode.timeline_panel import render_timeline_panel
from src.dashboard.live_mode.circuit_map import render_circuit_map

# =========================================================
# REPLAY MODE
# =========================================================
from src.dashboard.replay_mode.layout import render_replay_dashboard


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="F1 AI Race Strategy Dashboard",
    layout="wide"
)

fastf1.Cache.enable_cache("cache")


# =========================================================
# SESSION STATE INIT
# =========================================================

defaults = {
    "mode": None,
    "race_loop": None,
    "race_generator": None,
    "race_state": None,
    "research_data": None,
    "replay_data": None,
    "year": None,
    "gp": None,
    "driver": None,
    "circuit_len": None,
    "total_laps": None,
    "start_lap": None,
    "end_lap": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LAUNCH PANEL
# =========================================================

def launch_panel():

    st.title("🏁 F1 AI Race Strategy Decision Support System")

    st.markdown(
        "Configure race parameters before launching the AI strategy engine."
    )

    st.divider()

    st.subheader("Race Configuration")

    col1, col2 = st.columns(2)

    current_year = datetime.datetime.now().year
    seasons = list(range(2018, current_year + 1))

    season = None
    race = None
    driver = None

    with col1:

        season = st.selectbox(
            "Season",
            seasons,
            index=None,
            placeholder="Select Season"
        )

        if season:

            try:
                schedule = fastf1.get_event_schedule(season)
                race_list = schedule["EventName"].tolist()

                race = st.selectbox(
                    "Grand Prix",
                    race_list,
                    index=None,
                    placeholder="Select Grand Prix"
                )

            except Exception:
                race = st.text_input("Grand Prix")

        if season and race:

            try:
                session = fastf1.get_session(season, race, "R")
                session.load(laps=False)

                drivers = session.results["Abbreviation"].tolist()

            except Exception:
                drivers = ["VER", "PER", "HAM", "LEC", "NOR"]

            driver = st.selectbox(
                "Driver",
                drivers,
                index=None,
                placeholder="Select Driver"
            )

        circuit_len = st.number_input(
            "Circuit Length (km)",
            min_value=1.0,
            max_value=10.0,
            step=0.01
        )

    with col2:

        total_laps = st.number_input(
            "Total Race Laps",
            min_value=10,
            max_value=100,
            step=1
        )

        start_lap = st.number_input(
            "Start Lap",
            min_value=1,
            max_value=200,
            step=1
        )

        end_lap = st.number_input(
            "End Lap",
            min_value=1,
            max_value=200,
            step=1
        )

    st.divider()

    st.subheader("Select System Mode")

    col1, col2, col3 = st.columns(3)

    # =====================================================
    # RESEARCH MODE
    # =====================================================

    if col1.button("🔬 Research Mode"):

        if not season or not race or not driver:
            st.error("Please select Season, Race and Driver.")
            return

        config = {
            "season": season,
            "race": race,
            "driver": driver,
            "circuit_len": circuit_len,
            "total_laps": total_laps,
            "start_lap": 1,
            "end_lap": total_laps
        }

        pipeline = PipelineController()
        race_loop = pipeline.run("research", config)

        generator = race_loop.run()

        history_states = []

        try:
            while True:
                state = next(generator)
                history_states.append(state)
        except StopIteration:
            pass

        laps = []
        positions = []
        compounds = []
        pit_laps = []

        for state in history_states:

            for h in state.history:

                laps.append(h["lap"])
                positions.append(h["driver_position"])
                compounds.append(h["driver_tyre"])

                if h.get("decision") == "PIT NOW":
                    pit_laps.append(h["lap"])

        stints = []

        if laps and compounds:

            current_compound = compounds[0]
            start_lap = laps[0]

            for i in range(1, len(laps)):

                if compounds[i] != current_compound:

                    stints.append({
                        "compound": current_compound,
                        "start_lap": start_lap,
                        "end_lap": laps[i] - 1
                    })

                    current_compound = compounds[i]
                    start_lap = laps[i]

            stints.append({
                "compound": current_compound,
                "start_lap": start_lap,
                "end_lap": laps[-1]
            })

        mc = MonteCarloSimulator(200)

        outcomes = []

        for _ in range(100):

            base_time = np.random.normal(5200, 50)

            sim_result = SimulationResult(
                estimated_remaining_time=base_time,
                laps_simulated=total_laps,
                distance_simulated=300,
                pit=1
            )

            risk = mc.run(sim_result)

            outcomes.append(risk.mean_time)

        strategy_results = []

        test_pit_laps = [10, 15, 20, 25, 30]

        for pit in test_pit_laps:

            sim_time = 5200 - pit * 0.6 + np.random.normal(0, 10)

            strategy_results.append(
                {
                    "pit_lap": pit,
                    "mean_time": sim_time,
                    "risk": np.random.uniform(2, 6)
                }
            )

        research_results = {

            "pit_laps": pit_laps,
            "compounds": compounds,
            "stints": stints,
            "laps": laps,
            "positions": positions,
            "outcomes": outcomes,
            "strategy_results": strategy_results,
            "real_pit_laps": pit_laps,
            "total_laps": total_laps
        }

        st.session_state.research_data = research_results
        st.session_state.mode = "research"

        st.rerun()

    # =====================================================
    # REPLAY MODE
    # =====================================================

    if col2.button("📺 Replay Mode"):

        if not season or not race or not driver:
            st.error("Please select Season, Race and Driver.")
            return

        try:

            session = fastf1.get_session(season, race, "R")
            session.load()

            laps_df = session.laps.pick_driver(driver)

            laps = laps_df["LapNumber"].astype(int).tolist()

            real_pits = laps_df[laps_df["PitOutTime"].notna()]["LapNumber"].astype(int).tolist()

            tyre_life = laps_df["TyreLife"].fillna(0).values
            if len(tyre_life) == 0:
                tyre_life = np.zeros(len(laps))

            pit_probabilities = (tyre_life / (tyre_life.max() + 1e-6)).clip(0, 1)

            ai_center = int(np.median(laps)) if laps else None
            ai_pit_start = ai_center - 2 if ai_center else None
            ai_pit_end = ai_center + 2 if ai_center else None
            ai_pit_lap = ai_center

            real_pit_lap = real_pits[0] if real_pits else None

            lap_times = laps_df["LapTime"].dt.total_seconds().fillna(method="bfill")
            lap_delta = (lap_times - lap_times.mean()).tolist()

            true_positive = 1 if real_pit_lap and ai_pit_start <= real_pit_lap <= ai_pit_end else 0
            false_positive = 1 if real_pit_lap and not (ai_pit_start <= real_pit_lap <= ai_pit_end) else 0
            false_negative = 0 if real_pit_lap else 1

            replay_data = {
                "laps": laps,
                "pit_probabilities": pit_probabilities.tolist(),
                "ai_pit_start": ai_pit_start,
                "ai_pit_end": ai_pit_end,
                "ai_pit_lap": ai_pit_lap,
                "real_pit_lap": real_pit_lap,
                "lap_delta": lap_delta,
                "true_positive": true_positive,
                "false_positive": false_positive,
                "false_negative": false_negative
            }

            st.session_state.replay_data = replay_data
            st.session_state.mode = "replay"

            st.rerun()

        except Exception as e:
            st.error(f"Replay data loading failed: {e}")

    # =====================================================
    # LIVE MODE
    # =====================================================

    if col3.button("🏎 Live Strategy Mode"):

        if not season or not race or not driver:
            st.error("Please select Season, Race and Driver.")
            return

        st.session_state.mode = "strategy"

        config = {
            "season": season,
            "race": race,
            "driver": driver,
            "circuit_len": circuit_len,
            "total_laps": total_laps,
            "start_lap": start_lap,
            "end_lap": end_lap
        }

        pipeline = PipelineController()

        race_loop = pipeline.run("strategy", config)

        st.session_state.race_loop = race_loop
        st.session_state.race_generator = race_loop.run()
        st.session_state.race_state = None

        st.rerun()


# =========================================================
# LIVE DASHBOARD
# =========================================================

def strategy_dashboard():

    if st.button("⬅ Back to Main Menu"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.title("🏎️ F1 AI Race Strategy Decision Support System")

    st.divider()

    if st.session_state.race_generator:

        race_state = st.session_state.race_state

        if race_state is None:

            try:
                state = next(st.session_state.race_generator)
                st.session_state.race_state = state

            except StopIteration:
                st.success("Race Completed")
                return

        else:

            human_decision = getattr(race_state, "human_decision", None)

            if human_decision in ["y", "n"]:

                try:
                    state = next(st.session_state.race_generator)
                    st.session_state.race_state = state

                except StopIteration:
                    st.success("Race Completed")
                    return

    race_state = st.session_state.race_state

    if race_state is None:
        st.warning("Race has not started yet.")
        return

    left_col, center_col, right_col = st.columns([1.3, 1.8, 1.3])

    with left_col:
        render_state_panel(race_state)

    with center_col:

        decision = getattr(race_state, "ai_decision", None)

        if decision:
            render_decision_panel(decision)
        else:
            st.info("Waiting for AI strategy decision...")

    with right_col:

        mc_results = getattr(race_state, "mc_results", None)

        if mc_results:
            render_risk_panel(mc_results)
        else:
            st.info("Waiting for Monte Carlo simulation...")

    st.divider()

    bottom_left, bottom_right = st.columns([2, 1])

    with bottom_left:
        render_timeline_panel(race_state.history)

    with bottom_right:

        driver_progress = (
            race_state.distance_covered_km %
            race_state.lap_distance_km
        ) / race_state.lap_distance_km

        render_circuit_map(
            circuit_coords=None,
            driver_progress=driver_progress,
            teammate_progress=None
        )


# =========================================================
# MAIN ROUTER
# =========================================================

def main():

    if st.session_state.mode is None:
        launch_panel()

    elif st.session_state.mode == "strategy":
        strategy_dashboard()

    elif st.session_state.mode == "replay":

        if st.button("⬅ Back"):
            st.session_state.mode = None
            st.rerun()

        render_replay_dashboard(st.session_state.replay_data)

    elif st.session_state.mode == "research":

        if st.button("⬅ Back"):
            st.session_state.mode = None
            st.rerun()

        render_research_dashboard(st.session_state.research_data)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()