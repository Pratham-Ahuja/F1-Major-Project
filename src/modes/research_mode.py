import pandas as pd

from src.models.inference import run_inference
from src.simulation.strategy_simulator import StrategySimulator
from src.monte_carlo.monte_carlo_simulator import MonteCarloSimulator
from src.decision_support.decision_engine import DecisionEngine
from src.state.race_state import RaceState
from src.logging.ai_logger import AILogger

from src.race_dynamics.race_dynamics_engine import RaceDynamicsEngine
from src.position_model.position_predictor import PositionPredictor


class ResearchMode:
    """
    Research / experimentation mode.

    Used for analysing AI behaviour without human interaction.
    Produces detailed metrics useful for strategy experimentation.
    """

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
        self.total_laps = total_laps
        self.start_lap = start_lap
        self.end_lap = end_lap
        self.config = config

        # =====================================================
        # RACE STATE
        # =====================================================

        self.race_state = RaceState(
            current_lap=start_lap,
            lap_distance_km=circuit_length_km,
            total_laps_allowed=total_laps,
            analysis_start_lap=start_lap,
            analysis_end_lap=end_lap
        )

        # =====================================================
        # RACE DYNAMICS ENGINE (STEP 10)
        # =====================================================

        self.race_dynamics = RaceDynamicsEngine(self.race_state)

        # =====================================================
        # ENGINES
        # =====================================================

        self.strategy_simulator = StrategySimulator(
            processed_laps_df=self.features_df,
            race_state=self.race_state,
            race_engine=self.race_dynamics
        )

        self.monte_carlo = MonteCarloSimulator()

        self.decision_engine = DecisionEngine(config=self.config)

        self.position_predictor = PositionPredictor(self.race_dynamics)

        # =====================================================
        # LOGGER
        # =====================================================

        self.logger = AILogger(mode="research")

        # =====================================================
        # TRACKING VARIABLES
        # =====================================================

        self.ai_pit_laps = []
        self.laps_analyzed = 0

        print("Research Mode Initialized")

    # =====================================================
    # RUN RESEARCH ANALYSIS
    # =====================================================

    def run(self):

        for lap in range(self.start_lap, self.end_lap + 1):

            print(f"\n--- RESEARCH LAP {lap} ---")

            lap_df = self.features_df[
                self.features_df["LapNumber"] == lap
            ].copy()

            if lap_df.empty:
                break

            lap_row = lap_df.iloc[0]

            self.laps_analyzed += 1

            # =====================================================
            # INITIAL DRIVER STATE
            # =====================================================

            if lap == self.start_lap:

                self.race_state.update_driver_state(
                    position=int(lap_row.get("CurrentPosition", 10)),
                    tyre=str(lap_row.get("TyreCompound", "MEDIUM")),
                    tyre_life=int(lap_row.get("TyreLife", 1)),
                    stint=int(lap_row.get("Stint", 1))
                )

            else:

                self.race_state.driver_position = int(
                    lap_row.get("CurrentPosition", 10)
                )

                lap_df.loc[:, "TyreCompound"] = self.race_state.driver_tyre
                lap_df.loc[:, "TyreLife"] = self.race_state.driver_tyre_life
                lap_df.loc[:, "Stint"] = self.race_state.driver_stint

            # =====================================================
            # MODEL INFERENCE
            # =====================================================

            pit_prob_series, pit_decision_series = run_inference(
                self.model,
                lap_df
            )

            pit_prob = float(pit_prob_series.iloc[0])
            pit_decision = int(pit_decision_series.iloc[0])

            print(f"Pit Probability: {pit_prob:.3f}")

            # =====================================================
            # STRATEGY SIMULATION
            # =====================================================

            sim_result = self.strategy_simulator.simulate_strategy(
                pit=pit_decision
            )

            risk_metrics = self.monte_carlo.run(sim_result)

            # =====================================================
            # POSITION PREDICTION
            # =====================================================

            position_prediction = self.position_predictor.predict(lap_df)

            print("Projected Position if PIT:",
                  position_prediction.position_if_pit)

            print("Projected Position if STAY OUT:",
                  position_prediction.position_if_stay_out)

            print("Traffic Risk:",
                  position_prediction.traffic_risk)

            # =====================================================
            # DECISION ENGINE
            # =====================================================

            recommendation = self.decision_engine.generate(
                pit_probability=pit_prob,
                simulation_result=sim_result,
                risk_metrics=risk_metrics,
                position_prediction=position_prediction,
                current_lap=lap,
                current_tyre=self.race_state.driver_tyre,
                tyre_life=self.race_state.driver_tyre_life
            )

            print("Recommendation:", recommendation.action)

            # =====================================================
            # APPLY AI PIT (AUTOMATIC)
            # =====================================================

            if recommendation.action == "PIT NOW":

                self.ai_pit_laps.append(lap)

                new_tyre = recommendation.recommended_tyre

                new_position = self.race_dynamics.apply_pit(new_tyre)

                print(f"AI PIT EXECUTED → New Tyre: {new_tyre}")
                print(f"Position after pit: P{new_position}")

            else:

                self.race_dynamics.advance_lap()

            # =====================================================
            # LOGGING
            # =====================================================

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
                action=recommendation.action,
                confidence=recommendation.confidence,
                position_if_pit=position_prediction.position_if_pit,
                position_if_stay=position_prediction.position_if_stay_out,
                traffic_risk=position_prediction.traffic_risk,
                mean_time=risk_metrics.mean_time,
                std_dev=risk_metrics.std_dev
            )

            self.race_state.update_after_lap()

        # =====================================================
        # RESEARCH SUMMARY
        # =====================================================

        print("\n========== RESEARCH SUMMARY ==========")

        print("Total Laps Analysed:", self.laps_analyzed)

        print("AI Recommended Pit Laps:", self.ai_pit_laps)

        print("Total Recommended Stops:", len(self.ai_pit_laps))

        if self.ai_pit_laps:

            avg_stop_lap = sum(self.ai_pit_laps) / len(self.ai_pit_laps)

            print("Average Recommended Stop Lap:", round(avg_stop_lap, 2))

        print("Research Complete\n")