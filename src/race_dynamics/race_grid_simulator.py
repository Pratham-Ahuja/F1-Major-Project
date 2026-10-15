import random


class RaceGridSimulator:

    def __init__(self, drivers_list):

        self.drivers = {}

        for position, driver in enumerate(drivers_list, start=1):

            self.drivers[driver] = {
                "position": position,

                # cumulative race time
                "race_time": position * 0.3,

                "tyre_life": random.randint(1, 5),
                "tyre": "MEDIUM",
                "stint": 1,

                # store last lap time (helps future analytics)
                "last_lap_time": 90.0
            }

    # --------------------------------------------------
    # SIMULATE LAP
    # --------------------------------------------------

    def simulate_lap(self):

        for driver, state in self.drivers.items():

            base_time = 90

            degradation = state["tyre_life"] * 0.15

            randomness = random.uniform(-0.25, 0.25)

            lap_time = base_time + degradation + randomness

            # store lap time
            state["last_lap_time"] = lap_time

            # cumulative race time
            state["race_time"] += lap_time

            # tyre wear progression
            state["tyre_life"] += 1

        self.update_positions()

    # --------------------------------------------------
    # UPDATE POSITIONS
    # --------------------------------------------------

    def update_positions(self):

        ordered = sorted(
            self.drivers.items(),
            key=lambda x: x[1]["race_time"]
        )

        for pos, (driver, data) in enumerate(ordered, start=1):
            data["position"] = pos

    # --------------------------------------------------
    # APPLY PIT STOP
    # --------------------------------------------------

    def apply_pit(self, driver):

        if driver not in self.drivers:
            return

        state = self.drivers[driver]

        # realistic pit loss
        pit_loss = random.uniform(21.5, 24)

        state["race_time"] += pit_loss

        state["tyre_life"] = 0

        state["stint"] += 1

        self.update_positions()

    # --------------------------------------------------
    # GET POSITION
    # --------------------------------------------------

    def get_position(self, driver):

        if driver not in self.drivers:
            return None

        return self.drivers[driver]["position"]

    # --------------------------------------------------
    # GAP AHEAD
    # --------------------------------------------------

    def get_gap_ahead(self, driver):

        position = self.get_position(driver)

        if position <= 1:
            return None

        my_time = self.drivers[driver]["race_time"]

        for d, s in self.drivers.items():
            if s["position"] == position - 1:
                return round(abs(my_time - s["race_time"]), 2)

        return None

    # --------------------------------------------------
    # GAP BEHIND
    # --------------------------------------------------

    def get_gap_behind(self, driver):

        position = self.get_position(driver)

        if position >= len(self.drivers):
            return None

        my_time = self.drivers[driver]["race_time"]

        for d, s in self.drivers.items():
            if s["position"] == position + 1:
                return round(abs(s["race_time"] - my_time), 2)

        return None

    # --------------------------------------------------
    # TRAFFIC LEVEL
    # --------------------------------------------------

    def get_traffic_level(self, driver):

        position = self.get_position(driver)

        if position is None:
            return "UNKNOWN"

        if position >= 15:
            return "HIGH"

        if position >= 10:
            return "MEDIUM"

        return "LOW"