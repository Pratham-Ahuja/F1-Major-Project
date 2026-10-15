import numpy as np
from dataclasses import dataclass
from typing import List


# =========================================================
# RESULT OBJECT
# =========================================================
@dataclass
class EvaluationResult:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    total_ai_stops: int
    total_real_stops: int
    stop_difference: int
    avg_lap_delta: float


# =========================================================
# MODEL EVALUATOR
# =========================================================
class ModelEvaluator:
    """
    Evaluates AI strategy performance vs real race data.
    """

    def evaluate(
        self,
        ai_pit_laps: List[int],
        real_pit_laps: List[int],
        total_laps: int
    ) -> EvaluationResult:

        # ----------------------------------------------
        # Safety guard
        # ----------------------------------------------
        if total_laps <= 0:
            return EvaluationResult(0, 0, 0, 0, 0, 0, 0, 0)

        # ----------------------------------------------
        # Build binary arrays
        # ----------------------------------------------
        ai_array = np.zeros(total_laps)
        real_array = np.zeros(total_laps)

        for lap in ai_pit_laps:
            if 1 <= lap <= total_laps:
                ai_array[lap - 1] = 1

        for lap in real_pit_laps:
            if 1 <= lap <= total_laps:
                real_array[lap - 1] = 1

        # ----------------------------------------------
        # Confusion Matrix
        # ----------------------------------------------
        tp = np.sum((ai_array == 1) & (real_array == 1))
        tn = np.sum((ai_array == 0) & (real_array == 0))
        fp = np.sum((ai_array == 1) & (real_array == 0))
        fn = np.sum((ai_array == 0) & (real_array == 1))

        # ----------------------------------------------
        # Metrics
        # ----------------------------------------------
        accuracy = (tp + tn) / total_laps

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        # ----------------------------------------------
        # Strategy Metrics
        # ----------------------------------------------
        total_ai_stops = len(ai_pit_laps)
        total_real_stops = len(real_pit_laps)
        stop_difference = total_ai_stops - total_real_stops

        # Safer lap delta calculation
        lap_deltas = []
        min_length = min(total_ai_stops, total_real_stops)

        for i in range(min_length):
            lap_deltas.append(ai_pit_laps[i] - real_pit_laps[i])

        avg_lap_delta = float(np.mean(lap_deltas)) if lap_deltas else 0

        # ----------------------------------------------
        # Return Rounded Results (clean output)
        # ----------------------------------------------
        return EvaluationResult(
            accuracy=round(float(accuracy), 3),
            precision=round(float(precision), 3),
            recall=round(float(recall), 3),
            f1_score=round(float(f1), 3),
            total_ai_stops=total_ai_stops,
            total_real_stops=total_real_stops,
            stop_difference=stop_difference,
            avg_lap_delta=round(avg_lap_delta, 2)
        )