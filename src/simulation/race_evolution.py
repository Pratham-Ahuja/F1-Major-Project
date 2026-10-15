import random


class RaceEvolutionEngine:
    """
    Race evolution engine.

    Handles:
    - projected pit position
    - projected stay position
    - traffic estimation
    - applying pit stops
    - simple race progression
    - dynamic pit loss modelling
    """

    def __init__(self, race_state, circuit_length_km: float):

        self.race_state = race_state
        self.circuit_length_km = circuit_length_km

        self.grid_size = 20

        # --------------------------------------------------
        # STEP 9: dynamic pit loss calculation
        # --------------------------------------------------
        self.base_pit_loss_seconds = self._calculate_pit_loss()

    # --------------------------------------------------
    # PIT LOSS MODEL
    # --------------------------------------------------

    def _calculate_pit_loss(self):

        base = 20

        track_factor = self.circuit_length_km * 1.2

        pit_box_time = 2.5

        return base + track_factor + pit_box_time

    # --------------------------------------------------
    # PROJECT POSITION IF PIT
    # --------------------------------------------------

    def project_position_if_pit(self):

        current_position = self.race_state.driver_position

        # --------------------------------------------------
        # realistic pit drop model
        # --------------------------------------------------

        if current_position <= 3:
            drop = random.randint(8, 11)

        elif current_position <= 7:
            drop = random.randint(7, 10)

        elif current_position <= 12:
            drop = random.randint(6, 9)

        else:
            drop = random.randint(5, 7)

        new_position = current_position + drop

        if new_position > self.grid_size:
            new_position = self.grid_size

        traffic = self._estimate_traffic(new_position)

        return new_position, traffic

    # --------------------------------------------------
    # PROJECT POSITION IF STAY OUT
    # --------------------------------------------------

    def project_position_if_stay(self):

        current_position = self.race_state.driver_position
        tyre_life = self.race_state.driver_tyre_life

        # tyre degradation effects
        if tyre_life > 30:
            loss = random.randint(1, 3)

        elif tyre_life > 20:
            loss = random.randint(1, 2)

        elif tyre_life > 10:
            loss = random.randint(0, 1)

        else:
            loss = 0

        new_position = current_position + loss

        if new_position > self.grid_size:
            new_position = self.grid_size

        return new_position

    # --------------------------------------------------
    # TRAFFIC ESTIMATION
    # --------------------------------------------------

    def _estimate_traffic(self, position):

        if position >= 16:
            return "HIGH"

        elif position >= 10:
            return "MEDIUM"

        else:
            return "LOW"

    # --------------------------------------------------
    # APPLY PIT
    # --------------------------------------------------

    def apply_pit(self, new_tyre):

        rejoin_position, traffic = self.project_position_if_pit()

        self.race_state.driver_position = rejoin_position
        self.race_state.driver_tyre = new_tyre
        self.race_state.driver_tyre_life = 1
        self.race_state.driver_stint += 1

        return rejoin_position

    # --------------------------------------------------
    # ADVANCE LAP (NEW - used by race dynamics)
    # --------------------------------------------------

    def advance_lap(self):

        self.race_state.driver_tyre_life += 1

        new_position = self.project_position_if_stay()

        self.race_state.driver_position = new_position

        return new_position