from dataclasses import dataclass
import pandas as pd


# =========================================================
# POSITION PREDICTION RESULT OBJECT
# =========================================================

@dataclass
class PositionPrediction:
    position_if_pit: int
    position_if_stay_out: int
    positions_lost_if_pit: int
    traffic_risk: str


# =========================================================
# POSITION PREDICTOR ENGINE
# =========================================================

class PositionPredictor:
    """
    Predicts race position impact if driver pits vs stays out.

    Uses pit time physics:
    drivers within PIT_TIME seconds pass during pit stop.
    """

    PIT_TIME_LOSS_SECONDS = 23.0

    def __init__(self, race_dynamics_engine=None):

        # integration with race grid
        self.race_dynamics = race_dynamics_engine

    # -----------------------------------------------------
    # MAIN ENTRY POINT
    # -----------------------------------------------------
    def predict(self, lap_df: pd.DataFrame) -> PositionPrediction:

        row = lap_df.iloc[0]

        current_position = int(row.get("CurrentPosition", 10))

        # =====================================================
        # MODE 1 — GRID BASED PREDICTION
        # =====================================================

        if self.race_dynamics is not None:

            gap_behind = self.race_dynamics.grid.get_gap_behind(
                self.race_dynamics.ai_driver
            )

            # estimate number of drivers passing during pit
            if gap_behind is None:
                positions_lost_if_pit = 2
            else:
                positions_lost_if_pit = int(
                    min(
                        8,
                        max(
                            1,
                            gap_behind / 3
                        )
                    )
                )

            projected_pit_position = current_position + positions_lost_if_pit
            projected_pit_position = min(projected_pit_position, 20)

            projected_stay_position = current_position

            traffic_risk = self._traffic_from_position(projected_pit_position)

            return PositionPrediction(
                position_if_pit=projected_pit_position,
                position_if_stay_out=projected_stay_position,
                positions_lost_if_pit=positions_lost_if_pit,
                traffic_risk=traffic_risk
            )

        # =====================================================
        # MODE 2 — DATASET HEURISTIC
        # =====================================================

        gap_behind = float(row.get("GapBehind", 5.0))
        estimated_loss = int(row.get("EstimatedPositionLossIfPit", 2))

        positions_lost_if_pit = estimated_loss

        position_if_pit = current_position + positions_lost_if_pit
        position_if_pit = min(position_if_pit, 20)

        position_if_stay_out = current_position

        traffic_risk = self._traffic_from_position(position_if_pit)

        return PositionPrediction(
            position_if_pit=position_if_pit,
            position_if_stay_out=position_if_stay_out,
            positions_lost_if_pit=positions_lost_if_pit,
            traffic_risk=traffic_risk
        )

    # -----------------------------------------------------
    # TRAFFIC MODEL
    # -----------------------------------------------------
    def _traffic_from_position(self, position):

        if position >= 16:
            return "HIGH"

        if position >= 10:
            return "MEDIUM"

        return "LOW"