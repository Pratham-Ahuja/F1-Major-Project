import numpy as np
from dataclasses import dataclass


# =========================================================
# RESULT OBJECT (used by Monte Carlo & Decision Engine)
# =========================================================
@dataclass
class SimulationResult:
    estimated_remaining_time: float
    laps_simulated: int
    distance_simulated: float
    pit: int


# =========================================================
# STRATEGY SIMULATOR
# =========================================================
class StrategySimulator:
    """
    Deterministic strategy simulator
    (Race Evolution + Pit Physics version)
    """

    def __init__(self, processed_laps_df, race_state, race_engine=None):
        self.laps_df = processed_laps_df
        self.race_state = race_state
        self.race_engine = race_engine

    # =====================================================
    # SAFE NUMERIC HANDLER
    # =====================================================
    def _safe_float(self, value, default=0.0):
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    # =====================================================
    # PIT LOSS MODEL (STEP 9)
    # =====================================================
    def _calculate_dynamic_pit_loss(self):

        lap_distance = self._safe_float(
            getattr(self.race_state, "lap_distance_km", 5.0),
            5.0
        )

        # Base pit stop time
        base_pit = 20.0

        # Pit lane traversal effect
        track_factor = lap_distance * 1.2

        # Pit box service time
        pit_box_time = 2.5

        pit_loss = base_pit + track_factor + pit_box_time

        return pit_loss

    # =====================================================
    # PUBLIC API
    # =====================================================
    def simulate_strategy(self, pit: int) -> SimulationResult:
        """
        pit = 1 → simulate pit now
        pit = 0 → simulate stay out
        """

        if pit == 1:
            return self._simulate_pit()
        else:
            return self._simulate_no_pit()

    # =====================================================
    # CORE SIMULATION LOOP
    # =====================================================
    def _simulate_remaining_race(self, starting_tyre_life, pit_loss):

        total_laps_allowed = self._safe_float(
            getattr(self.race_state, "total_laps_allowed", 0),
            0
        )

        current_lap = self._safe_float(
            getattr(self.race_state, "current_lap", 0),
            0
        )

        lap_distance = self._safe_float(
            getattr(self.race_state, "lap_distance_km", 5.0),
            5.0
        )

        distance_covered = self._safe_float(
            getattr(self.race_state, "distance_covered_km", 0),
            0
        )

        laps_remaining = max(int(total_laps_allowed - current_lap), 0)

        tyre_life = int(self._safe_float(starting_tyre_life, 1))
        pit_loss = self._safe_float(pit_loss, 0.0)

        total_time = 0.0

        # -------------------------------------
        # Simulation Loop
        # -------------------------------------
        for lap in range(laps_remaining):

            # FIA 308 km race limit safeguard
            if distance_covered >= 308:
                break

            base_lap_time = 90.0

            # Tyre degradation model
            degradation_penalty = tyre_life * 0.15

            # STEP 9: tyre warmup penalty
            warmup_penalty = 0.0
            if tyre_life <= 2:
                warmup_penalty = 1.2

            lap_time = base_lap_time + degradation_penalty + warmup_penalty

            # numeric validation
            if np.isnan(lap_time) or np.isinf(lap_time):
                raise ValueError("Invalid lap_time produced in simulator")

            total_time += lap_time
            tyre_life += 1
            distance_covered += lap_distance

        total_time += pit_loss

        if np.isnan(total_time) or np.isinf(total_time):
            raise ValueError("Invalid total_time produced in simulator")

        return SimulationResult(
            estimated_remaining_time=float(total_time),
            laps_simulated=int(laps_remaining),
            distance_simulated=float(distance_covered),
            pit=int(pit_loss > 0)
        )

    # =====================================================
    # PIT SCENARIO
    # =====================================================
    def _simulate_pit(self):

        # Use race engine pit loss if available
        if self.race_engine is not None:
            pit_loss = getattr(self.race_engine, "base_pit_loss_seconds", None)

            if pit_loss is None:
                pit_loss = self._calculate_dynamic_pit_loss()

        else:
            pit_loss = self._calculate_dynamic_pit_loss()

        return self._simulate_remaining_race(
            starting_tyre_life=1,
            pit_loss=pit_loss
        )

    # =====================================================
    # NO PIT SCENARIO
    # =====================================================
    def _simulate_no_pit(self):

        tyre_life = getattr(self.race_state, "driver_tyre_life", 5)

        return self._simulate_remaining_race(
            starting_tyre_life=tyre_life,
            pit_loss=0.0
        )