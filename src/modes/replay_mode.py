import pandas as pd

from src.models.inference import run_inference
from src.simulation.strategy_simulator import StrategySimulator
from src.monte_carlo.monte_carlo_simulator import MonteCarloSimulator
from src.decision_support.decision_engine import DecisionEngine
from src.state.race_state import RaceState
from src.logging.ai_logger import AILogger
from src.evaluation.model_evaluator import ModelEvaluator

from src.race_dynamics.race_dynamics_engine import RaceDynamicsEngine
from src.position_model.position_predictor import PositionPredictor


class ReplayMode:
    """
    Historical replay mode.

    - No human input
    - Uses real historical pit laps
    - Logs AI recommendation vs actual action
    - Performs formal model evaluation
    """

    def __init__(
        self,
        features_df: pd.DataFrame,
        trained_model,
        total_laps: int,
        circuit_length_km: float,
        config=None
    ):

        self.features_df = features_df
        self.model = trained_model
        self.total_laps = total_laps
        self.config = config

        # =====================================================
        # RACE STATE
        # =====================================================

        self.race_state = RaceState(
            current_lap=1,
            lap_distance_km=circuit_length_km,
            total_laps_allowed=total_laps,
            analysis_start_lap=1,
            analysis_end_lap=total_laps
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

        self.logger = AILogger(mode="replay")

        # =====================================================
        # MODEL EVALUATOR
        # =====================================================

        self.evaluator = ModelEvaluator()

        self.ai_pit_laps = []
        self.actual_pit_laps = []

        print("Replay Mode Initialized")

    # =====================================================
    # RUN REPLAY
    # =====================================================

    def run(self):

        for lap in range(1, self.total_laps + 1):

            print(f"\n--- REPLAY LAP {lap} ---")

            lap_df = self.features_df[
                self.features_df["LapNumber"] == lap
            ].copy()

            if lap_df.empty:
                break

            lap_row = lap_df.iloc[0]

            actual_stint = int(lap_row.get("Stint", 1))

            # =====================================================
            # INITIAL DRIVER STATE
            # =====================================================

            if lap == 1:

                self.race_state.update_driver_state(
                    position=int(lap_row.get("CurrentPosition", 10)),
                    tyre=str(lap_row.get("TyreCompound", "MEDIUM")),
                    tyre_life=int(lap_row.get("TyreLife", 1)),
                    stint=actual_stint
                )

                previous_stint = actual_stint

            else:
                previous_stint = self.race_state.driver_stint

            # =====================================================
            # REAL PIT DETECTION
            # =====================================================

            if actual_stint > previous_stint:
                self.actual_pit_laps.append(lap)

            # =====================================================
            # FEATURE UPDATE FROM RACE STATE
            # =====================================================

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

            if recommendation.action == "PIT NOW":
                self.ai_pit_laps.append(lap)

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

            # =====================================================
            # APPLY REAL PIT
            # =====================================================

            if actual_stint > self.race_state.driver_stint:

                new_tyre = str(lap_row.get("TyreCompound", "MEDIUM"))

                new_position = self.race_dynamics.apply_pit(new_tyre)

                print(f"Real pit detected. New tyre: {new_tyre}")
                print(f"Position after pit: P{new_position}")

            else:

                self.race_dynamics.advance_lap()

            self.race_state.update_after_lap()

        # =====================================================
        # SUMMARY
        # =====================================================

        print("\n========== REPLAY SUMMARY ==========")

        print("AI Pit Laps:", self.ai_pit_laps)
        print("Actual Pit Laps:", self.actual_pit_laps)

        if self.actual_pit_laps:

            delta = [
                ai - real
                for ai, real in zip(self.ai_pit_laps, self.actual_pit_laps)
            ]

            print("Lap Delta (AI - Real):", delta)

        # =====================================================
        # MODEL EVALUATION
        # =====================================================

        evaluation_result = self.evaluator.evaluate(
            ai_pit_laps=self.ai_pit_laps,
            real_pit_laps=self.actual_pit_laps,
            total_laps=self.total_laps
        )

        print("\n----- MODEL PERFORMANCE -----")
        print("Accuracy:", round(evaluation_result.accuracy, 3))
        print("Precision:", round(evaluation_result.precision, 3))
        print("Recall:", round(evaluation_result.recall, 3))
        print("F1 Score:", round(evaluation_result.f1_score, 3))
        print("Total AI Stops:", evaluation_result.total_ai_stops)
        print("Total Real Stops:", evaluation_result.total_real_stops)
        print("Stop Difference:", evaluation_result.stop_difference)
        print("Avg Lap Delta:", evaluation_result.avg_lap_delta)

        print("Replay Complete\n")