import pandas as pd
import numpy as np

from src.models.inference import run_inference
from src.simulation.strategy_simulator import StrategySimulator
from src.monte_carlo.monte_carlo_simulator import MonteCarloSimulator
from src.decision_support.decision_engine import DecisionEngine
from src.state.race_state import RaceState
from src.logging.ai_logger import AILogger

from src.race_dynamics.race_dynamics_engine import RaceDynamicsEngine
from src.position_model.position_predictor import PositionPredictor


class RaceLoop:

    def __init__(
        self,
        features_df: pd.DataFrame,
        trained_model,
        total_laps: int,
        circuit_length_km: float,
        start_lap: int,
        end_lap: int,
        config=None
    ):

        self.features_df = features_df
        self.model = trained_model
        self.start_lap = start_lap
        self.end_lap = end_lap
        self.config = config

        self.race_state = RaceState(
            current_lap=start_lap,
            lap_distance_km=circuit_length_km,
            total_laps_allowed=total_laps,
            analysis_start_lap=start_lap,
            analysis_end_lap=end_lap
        )

        self.race_state.human_decision = "n"
        self.race_state.pending_pit = False

        self.race_dynamics = RaceDynamicsEngine(self.race_state)

        self.strategy_simulator = StrategySimulator(
            processed_laps_df=self.features_df,
            race_state=self.race_state,
            race_engine=self.race_dynamics
        )

        self.monte_carlo = MonteCarloSimulator()
        self.decision_engine = DecisionEngine(config=self.config)
        self.position_predictor = PositionPredictor(self.race_dynamics)

        self.logger = AILogger(mode="live")

        print("Live Race Loop Initialized")

    # -----------------------------------------------------

    def run(self):

        for lap in range(self.start_lap, self.end_lap + 1):

            print(f"\n--- LAP {lap} ---")

            lap_df = self.features_df[
                self.features_df["LapNumber"] == lap
            ].copy()

            # ✅ FIX 1: DO NOT BREAK LOOP
            if lap_df.empty:
                print("No lap data available. Using last known state.")

                lap_row = {
                    "TyreCompound": self.race_state.driver_tyre,
                    "TyreLife": self.race_state.driver_tyre_life,
                    "Stint": self.race_state.driver_stint,
                    "GapAhead": 2.5,
                    "GapBehind": 3.0
                }

                lap_df = pd.DataFrame([lap_row])
            else:
                lap_row = lap_df.iloc[0]

            # -----------------------------------------------
            # INITIAL DRIVER STATE
            # -----------------------------------------------

            if lap == self.start_lap:

                starting_tyre = str(lap_row.get("TyreCompound", "MEDIUM"))
                starting_tyre_life = int(lap_row.get("TyreLife", 1))
                starting_stint = int(lap_row.get("Stint", 1))

                self.race_state.update_driver_state(
                    position=int(lap_row.get("CurrentPosition", 10)),
                    tyre=starting_tyre,
                    tyre_life=starting_tyre_life,
                    stint=starting_stint
                )

            else:

                # ✅ FIX 2: REAL PIT DETECTION (NO OVERWRITE BUG)

                telemetry_life = int(
                    lap_row.get("TyreLife", self.race_state.driver_tyre_life)
                )

                if telemetry_life < self.race_state.driver_tyre_life:

                    print("Real pit detected")

                    self.race_state.driver_tyre = str(
                        lap_row.get("TyreCompound", self.race_state.driver_tyre)
                    )

                    self.race_state.driver_tyre_life = telemetry_life
                    self.race_state.driver_stint = int(
                        lap_row.get("Stint", self.race_state.driver_stint)
                    )

                    self.race_state.recent_pit = True

                else:

                    if not self.race_state.recent_pit:

                        self.race_state.driver_tyre = str(
                            lap_row.get("TyreCompound", self.race_state.driver_tyre)
                        )

                        self.race_state.driver_tyre_life = telemetry_life

                        self.race_state.driver_stint = int(
                            lap_row.get("Stint", self.race_state.driver_stint)
                        )

                lap_df.loc[:, "TyreCompound"] = self.race_state.driver_tyre
                lap_df.loc[:, "TyreLife"] = self.race_state.driver_tyre_life
                lap_df.loc[:, "Stint"] = self.race_state.driver_stint

            # -----------------------------------------------
            # MODEL INFERENCE
            # -----------------------------------------------

            pit_prob_series, pit_decision_series = run_inference(
                self.model,
                lap_df
            )

            pit_prob = float(pit_prob_series.iloc[0])
            pit_decision = int(pit_decision_series.iloc[0])

            # -----------------------------------------------
            # STRATEGY SIMULATION
            # -----------------------------------------------

            sim_result = self.strategy_simulator.simulate_strategy(
                pit=pit_decision
            )

            # -----------------------------------------------
            # MONTE CARLO
            # -----------------------------------------------

            risk_metrics = self.monte_carlo.run(sim_result)

            # -----------------------------------------------
            # POSITION PREDICTION
            # -----------------------------------------------

            position_prediction = self.position_predictor.predict(lap_df)

            # -----------------------------------------------
            # DECISION ENGINE
            # -----------------------------------------------

            recommendation = self.decision_engine.generate(
                pit_probability=pit_prob,
                simulation_result=sim_result,
                risk_metrics=risk_metrics,
                position_prediction=position_prediction,
                current_lap=lap,
                current_tyre=self.race_state.driver_tyre,
                tyre_life=self.race_state.driver_tyre_life
            )

            # =================================================
            # STRATEGY RULES
            # =================================================

            laps_remaining = self.end_lap - lap

            if laps_remaining <= 5:
                recommendation.action = "STAY OUT"

            if self.race_state.pending_pit and not self.race_state.recent_pit:
                recommendation.action = "PIT NOW"

            pit_window_start = int(self.end_lap * 0.25)
            pit_window_end = int(self.end_lap * 0.75)

            if pit_window_start <= lap <= pit_window_end:
                recommendation.strategy_type = "UNDERCUT"
            else:
                recommendation.strategy_type = "EXTEND"

            if recommendation.action == "PIT NOW":
                self.race_state.pending_pit = True

            self.race_state.ai_decision = recommendation

            # -----------------------------------------------
            # MONTE CARLO PANEL FORMAT
            # -----------------------------------------------

            mean_time = getattr(risk_metrics, "mean_time", None)
            std_dev = getattr(risk_metrics, "std_dev", None)
            outcomes = getattr(risk_metrics, "outcomes", None)

            if outcomes is None or len(outcomes) == 0:

                if mean_time is not None and std_dev is not None:
                    outcomes = np.random.normal(mean_time, std_dev, 500)
                else:
                    outcomes = []

            self.race_state.mc_results = {
                "outcomes": outcomes,
                "best_case": float(np.min(outcomes)) if len(outcomes) else None,
                "expected_case": mean_time,
                "worst_case": float(np.max(outcomes)) if len(outcomes) else None,
                "risk_level": getattr(recommendation, "risk_level", "UNKNOWN")
            }

            # -----------------------------------------------
            # LOGGER
            # -----------------------------------------------

            adjusted_probability = (
                pit_prob * self.config.strategy_profile.aggression_multiplier
                if self.config else pit_prob
            )

            self.logger.log_lap(
                lap=lap,
                pit_probability=pit_prob,
                adjusted_probability=adjusted_probability,
                strategy_profile=self.config.strategy_profile.name
                if self.config else "Default",
                current_tyre=self.race_state.driver_tyre,
                tyre_life=self.race_state.driver_tyre_life,
                action=getattr(recommendation, "action", "UNKNOWN"),
                confidence=getattr(recommendation, "confidence", 0.0),
                position_if_pit=position_prediction.position_if_pit,
                position_if_stay=position_prediction.position_if_stay_out,
                traffic_risk=position_prediction.traffic_risk,
                mean_time=risk_metrics.mean_time,
                std_dev=risk_metrics.std_dev
            )

            # -----------------------------------------------
            # HUMAN DECISION
            # -----------------------------------------------

            did_pit = getattr(self.race_state, "human_decision", "n")

            if did_pit == "y":

                new_tyre = getattr(recommendation, "recommended_tyre", "MEDIUM")

                new_position = self.race_dynamics.apply_pit(new_tyre)

                print(f"Driver pitted. New tyre fitted: {new_tyre}")
                print(f"New position after pit: P{new_position}")

                self.race_state.recent_pit = True
                self.race_state.pending_pit = False
                self.race_state.ai_decision = None

            else:

                self.race_dynamics.advance_lap()
                self.race_state.recent_pit = False

            # -----------------------------------------------
            # ADVANCE RACE STATE
            # -----------------------------------------------

            self.race_state.update_after_lap()

            # -----------------------------------------------
            # TIMELINE HISTORY
            # -----------------------------------------------

            self.race_state.history.append({
                "lap": lap,
                "driver_position": self.race_state.driver_position,
                "driver_tyre": self.race_state.driver_tyre,
                "driver_tyre_life": self.race_state.driver_tyre_life,
                "decision": getattr(recommendation, "action", "UNKNOWN"),
                "confidence": getattr(recommendation, "confidence", 0.0),
                "strategy_type": getattr(recommendation, "strategy_type", "STANDARD")
            })

            yield self.race_state

            self.race_state.human_decision = "n"

        print("\nRace simulation complete.")