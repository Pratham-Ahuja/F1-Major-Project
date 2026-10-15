import os
import csv
from datetime import datetime


class AILogger:

    def __init__(self, mode: str):

        self.mode = mode.lower()

        # Create logs directory if not exists
        os.makedirs("logs", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.file_path = f"logs/{self.mode}_session_{timestamp}.csv"

        self._create_file()

    # --------------------------------------------------
    def _create_file(self):

        headers = [
            "Lap",
            "PitProbability",
            "AdjustedProbability",
            "StrategyProfile",
            "CurrentTyre",
            "TyreLife",
            "RecommendedAction",
            "Confidence",
            "PositionIfPit",
            "PositionIfStay",
            "TrafficRisk",
            "ExpectedRemainingTime",
            "RiskStdDev"
        ]

        with open(self.file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

    # --------------------------------------------------
    def log_lap(
        self,
        lap,
        pit_probability,
        adjusted_probability,
        strategy_profile,
        current_tyre,
        tyre_life,
        action,
        confidence,
        position_if_pit,
        position_if_stay,
        traffic_risk,
        mean_time,
        std_dev
    ):

        row = [
            lap,
            pit_probability,
            adjusted_probability,
            strategy_profile,
            current_tyre,
            tyre_life,
            action,
            confidence,
            position_if_pit,
            position_if_stay,
            traffic_risk,
            mean_time,
            std_dev
        ]

        with open(self.file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)