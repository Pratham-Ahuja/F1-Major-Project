from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


# ==================================================
# GLOBAL RACE CONSTANTS
# ==================================================

PIT_TOTAL_TIME = 23                # 3s pit stop + 20s pit lane
MIN_LAPS_AFTER_PIT = 5             # Pit cooldown rule
MANDATORY_COMPOUNDS_REQUIRED = 2   # FIA dry tyre rule


@dataclass
class RaceState:
    """
    Central race state container.
    Single source of truth for live / simulated race execution.
    """

    # ==================================================
    # Race-level structure
    # ==================================================
    current_lap: int
    analysis_start_lap: int
    analysis_end_lap: int
    lap_distance_km: float
    total_laps_allowed: int

    distance_covered_km: float = 0.0

    # ==================================================
    # Focus driver
    # ==================================================
    driver_id: str = ""
    driver_position: Optional[int] = None
    driver_tyre: Optional[str] = None
    driver_tyre_life: Optional[int] = None
    driver_stint: Optional[int] = None

    # memory of recent pit stop
    recent_pit: bool = False

    # last pit tracking (for cooldown rule)
    last_pit_lap: int = -999
    laps_since_last_pit: int = 999

    # compounds used during race
    used_compounds: Set[str] = field(default_factory=set)

    # human decision for dashboard interaction
    human_decision: str = "n"

    # ==================================================
    # Teammate context
    # ==================================================
    teammate_id: Optional[str] = None
    teammate_position: Optional[int] = None

    # ==================================================
    # Traffic & gap state
    # ==================================================
    gap_ahead_seconds: Optional[float] = None
    gap_behind_seconds: Optional[float] = None
    traffic_density: Optional[str] = None

    # ==================================================
    # Environment snapshot
    # ==================================================
    weather_snapshot: Optional[Dict] = None

    # ==================================================
    # History logging
    # ==================================================
    history: List[Dict] = field(default_factory=list)

    # ==================================================
    # LAP PROGRESSION
    # ==================================================
    def update_after_lap(self):
        """
        Progress race by one lap.
        Handles distance, tyre ageing and pit cooldown updates.
        """

        if self.is_race_complete():
            return

        # Advance lap
        self.current_lap += 1

        # Update distance
        self.distance_covered_km += self.lap_distance_km

        # Tyre ageing
        if self.driver_tyre_life is not None:
            self.driver_tyre_life += 1

        # Update pit cooldown tracking
        self.laps_since_last_pit = self.current_lap - self.last_pit_lap

        # Reset pit flag after lap completed
        self.recent_pit = False

    # ==================================================
    # RACE END CHECK
    # ==================================================
    def is_race_complete(self) -> bool:
        """
        Determine whether race simulation has finished.
        """

        return (
            self.current_lap > self.analysis_end_lap
            or self.current_lap >= self.total_laps_allowed
            or self.distance_covered_km >= 308.0
        )

    # ==================================================
    # DRIVER STATE
    # ==================================================
    def update_driver_state(self, position: int, tyre: str, tyre_life: int, stint: int):
        """
        Update driver telemetry from simulation / dataset.
        """

        self.driver_position = position
        self.driver_tyre = tyre
        self.driver_tyre_life = tyre_life
        self.driver_stint = stint

        if tyre is not None:
            self.used_compounds.add(tyre)

    def update_teammate_state(self, position: int):
        self.teammate_position = position

    # ==================================================
    # TRAFFIC STATE
    # ==================================================
    def update_traffic_state(self, gap_ahead: Optional[float], gap_behind: Optional[float]):

        self.gap_ahead_seconds = gap_ahead
        self.gap_behind_seconds = gap_behind

        if gap_ahead is None or gap_behind is None:
            self.traffic_density = None
        elif gap_ahead < 1.5 and gap_behind < 1.5:
            self.traffic_density = "HIGH"
        elif gap_ahead < 3.0:
            self.traffic_density = "MEDIUM"
        else:
            self.traffic_density = "LOW"

    # ==================================================
    # WEATHER STATE
    # ==================================================
    def update_weather(self, weather_data: Dict):
        self.weather_snapshot = weather_data

    # ==================================================
    # PIT STOP HANDLING
    # ==================================================
    def apply_pit_stop(self, new_tyre: str):
        """
        Apply pit stop logic.
        Handles tyre reset, stint increment and cooldown tracking.
        """

        self.driver_tyre = new_tyre
        self.driver_tyre_life = 0
        self.recent_pit = True

        # Track compound usage
        self.used_compounds.add(new_tyre)

        # Update stint
        if self.driver_stint is None:
            self.driver_stint = 1
        else:
            self.driver_stint += 1

        # Record pit lap
        self.last_pit_lap = self.current_lap
        self.laps_since_last_pit = 0

        print(f"Driver pitted. New tyre fitted: {new_tyre}")

    # ==================================================
    # PIT COOLDOWN RULE
    # ==================================================
    def pit_cooldown_active(self) -> bool:
        """
        Prevent immediate consecutive pit stops.
        """

        return self.laps_since_last_pit < MIN_LAPS_AFTER_PIT

    # ==================================================
    # MANDATORY TYRE RULE
    # ==================================================
    def compound_rule_violation(self) -> bool:
        """
        Enforce FIA rule requiring two compounds in race.
        """

        if len(self.used_compounds) >= MANDATORY_COMPOUNDS_REQUIRED:
            return False

        laps_remaining = self.total_laps_allowed - self.current_lap

        # Force compound change near race end
        if laps_remaining <= 10:
            return True

        return False

    # ==================================================
    # POSITION LOSS DURING PIT
    # ==================================================
    def calculate_position_loss(self) -> int:
        """
        Calculate number of positions lost during pit stop
        using the 23 second pit window rule.
        """

        if self.gap_behind_seconds is None:
            return 0

        if self.gap_behind_seconds < PIT_TOTAL_TIME:
            return 1

        return 0

    # ==================================================
    # HISTORY LOGGING
    # ==================================================
    def log_state(self, decision: str = "UNKNOWN", confidence: float = 0.0):
        """
        Log race state snapshot for timeline panel.
        """

        snapshot = {
            "lap": self.current_lap,
            "distance_covered_km": self.distance_covered_km,
            "driver_position": self.driver_position,
            "driver_tyre": self.driver_tyre,
            "driver_tyre_life": self.driver_tyre_life,
            "driver_stint": self.driver_stint,
            "decision": decision,
            "confidence": confidence,
            "weather": self.weather_snapshot
        }

        self.history.append(snapshot)