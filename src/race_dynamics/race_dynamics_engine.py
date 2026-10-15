import random
from src.race_dynamics.race_grid_simulator import RaceGridSimulator


class RaceDynamicsEngine:

    """
    Handles race evolution:
    - pit outcome
    - position change
    - traffic modelling
    - full race grid simulation
    - position regain model
    """

    PIT_TIME_SECONDS = 23
    POSITION_REGAIN_RATE = 0.35

    def __init__(self, race_state):

        self.race_state = race_state

        # --------------------------------------------
        # CREATE RACE GRID (20 drivers)
        # --------------------------------------------

        drivers = [f"DRIVER_{i}" for i in range(1, 21)]

        # First driver is our AI driver
        self.ai_driver = drivers[0]

        self.grid = RaceGridSimulator(drivers)

        # Store target regain position
        self.target_position = None

    # ============================================
    # APPLY PIT EVENT
    # ============================================

    def apply_pit(self, recommended_tyre):

        """
        Apply pit stop to AI driver.
        Includes position loss simulation.
        """

        # Apply pit physics in race grid
        self.grid.apply_pit(self.ai_driver)

        # Reset tyre
        self.race_state.driver_tyre = recommended_tyre
        self.race_state.driver_tyre_life = 0

        # Update stint safely
        if self.race_state.driver_stint is None:
            self.race_state.driver_stint = 1
        else:
            self.race_state.driver_stint += 1

        # Get updated position from grid
        new_position = self.grid.get_position(self.ai_driver)

        self.race_state.driver_position = new_position

        # Target regain position (pre-pit position)
        self.target_position = max(1, new_position - 5)

        # Update traffic
        self._update_traffic()

        return new_position

    # ============================================
    # ADVANCE LAP (FULL GRID SIMULATION)
    # ============================================

    def advance_lap(self):

        """
        Simulate one full lap for the entire race grid.
        """

        # Simulate lap for all drivers
        self.grid.simulate_lap()

        # Current position from grid
        new_position = self.grid.get_position(self.ai_driver)

        # Apply regain model
        new_position = self._apply_position_regain(new_position)

        self.race_state.driver_position = new_position

        # Update traffic context
        self._update_traffic()

    # ============================================
    # POSITION REGAIN MODEL
    # ============================================

    def _apply_position_regain(self, current_position):

        """
        Gradually regain positions after pit stop.
        """

        if self.target_position is None:
            return current_position

        if current_position <= self.target_position:
            return current_position

        regain_step = random.random()

        if regain_step < self.POSITION_REGAIN_RATE:
            current_position -= 1

        return max(1, current_position)

    # ============================================
    # TRAFFIC MODEL
    # ============================================

    def _update_traffic(self):

        """
        Update gap and traffic conditions in race state.
        """

        gap_ahead = self.grid.get_gap_ahead(self.ai_driver)
        gap_behind = self.grid.get_gap_behind(self.ai_driver)

        self.race_state.update_traffic_state(
            gap_ahead,
            gap_behind
        )

    # ============================================
    # TRAFFIC LEVEL
    # ============================================

    def simulate_traffic(self):

        """
        Return traffic level for AI driver.
        """

        return self.grid.get_traffic_level(self.ai_driver)