from dataclasses import dataclass
from src.monte_carlo.monte_carlo_simulator import RiskMetrics
from src.simulation.strategy_simulator import SimulationResult


# =========================================================
# STRATEGY RECOMMENDATION OBJECT
# =========================================================
@dataclass
class StrategyRecommendation:
    action: str
    confidence: float
    explanation: str
    current_tyre: str
    recommended_tyre: str
    strategy_type: str
    risk_level: str


# =========================================================
# DECISION ENGINE
# =========================================================
class DecisionEngine:

    TYRE_MAX_LIFE = {
        "HARD": 32,
        "MEDIUM": 24,
        "SOFT": 14
    }

    def __init__(self, config=None):
        self.last_pit_lap = -999
        self.config = config

    # --------------------------------------------------
    # TYRE SELECTION
    # --------------------------------------------------
    def _choose_best_tyre(self, laps_remaining):

        if laps_remaining > 30:
            return "HARD"

        elif laps_remaining > 15:
            return "MEDIUM"

        else:
            return "SOFT"

    # --------------------------------------------------
    # PIT COOLDOWN RULE
    # --------------------------------------------------
    def _cooldown_active(self, current_lap):

        laps_since_last_pit = current_lap - self.last_pit_lap
        return laps_since_last_pit <= 6

    # --------------------------------------------------
    # FINAL STINT RULE
    # --------------------------------------------------
    def _can_finish_race(self, current_tyre, tyre_life, laps_remaining):

        max_life = self.TYRE_MAX_LIFE.get(current_tyre, 20)
        laps_left_on_tyre = max_life - tyre_life

        return laps_remaining <= laps_left_on_tyre

    # --------------------------------------------------
    # MAIN DECISION
    # --------------------------------------------------
    def generate(
        self,
        pit_probability,
        simulation_result: SimulationResult,
        risk_metrics: RiskMetrics,
        position_prediction,
        current_lap,
        current_tyre="MEDIUM",
        tyre_life=1
    ):

        laps_remaining = simulation_result.laps_simulated
        explanation_parts = []

        # --------------------------------------------------
        # STRATEGY PROFILE THRESHOLD
        # --------------------------------------------------
        threshold = 0.55

        if self.config:
            threshold = self.config.strategy_profile.pit_threshold

        # --------------------------------------------------
        # POSITION IMPACT
        # --------------------------------------------------
        position_loss = (
            position_prediction.position_if_pit
            - position_prediction.position_if_stay_out
        )

        # ==================================================
        # NEW RULE — TYRE WEAR WINDOW (COMPOUND DEPENDENT)
        # ==================================================
        max_life = self.TYRE_MAX_LIFE.get(current_tyre, 20)

        wear_ratio = tyre_life / max_life

        # tyre optimal zone
        if wear_ratio < 0.65:
            pass

        # pit window
        elif wear_ratio < 1.0:
            if pit_probability > 0.35:
                action = "PIT NOW"
                strategy_type = "UNDERCUT"
                explanation_parts.append("Tyre in pit window")
            else:
                action = "STAY OUT"
                strategy_type = "EXTEND"
                explanation_parts.append("Extending tyre stint")

            confidence = min(
                1.0,
                pit_probability + (risk_metrics.std_dev / 10)
            )

            recommended_tyre = self._choose_best_tyre(laps_remaining)

            risk_level = "LOW" if risk_metrics.std_dev <= 2 else "MEDIUM" if risk_metrics.std_dev <= 4 else "HIGH"

            explanation = (
                f"Pit probability: {pit_probability:.2f} | "
                f"Tyre wear: {tyre_life}/{max_life} | "
                f"Position loss if PIT: {position_loss} | "
                f"Traffic: {position_prediction.traffic_risk} | "
                f"Risk spread: ±{risk_metrics.std_dev:.1f}s | "
                + ", ".join(explanation_parts)
            )

            return StrategyRecommendation(
                action=action,
                confidence=confidence,
                explanation=explanation,
                current_tyre=current_tyre,
                recommended_tyre=recommended_tyre,
                strategy_type=strategy_type,
                risk_level=risk_level
            )

        # extended stint (stretch tyre)
        elif wear_ratio < 1.2:
            action = "STAY OUT"
            strategy_type = "OVERCUT"
            explanation_parts.append("Tyre beyond optimal life, extending stint")

            confidence = min(
                1.0,
                pit_probability + (risk_metrics.std_dev / 10)
            )

            recommended_tyre = self._choose_best_tyre(laps_remaining)

            risk_level = "LOW" if risk_metrics.std_dev <= 2 else "MEDIUM" if risk_metrics.std_dev <= 4 else "HIGH"

            explanation = (
                f"Pit probability: {pit_probability:.2f} | "
                f"Tyre wear: {tyre_life}/{max_life} | "
                f"Position loss if PIT: {position_loss} | "
                f"Traffic: {position_prediction.traffic_risk} | "
                f"Risk spread: ±{risk_metrics.std_dev:.1f}s | "
                + ", ".join(explanation_parts)
            )

            return StrategyRecommendation(
                action=action,
                confidence=confidence,
                explanation=explanation,
                current_tyre=current_tyre,
                recommended_tyre=recommended_tyre,
                strategy_type=strategy_type,
                risk_level=risk_level
            )

        # critical tyre state
        elif wear_ratio >= 1.2:
            action = "PIT NOW"
            strategy_type = "FORCED PIT"
            explanation_parts.append("Tyre critical wear level")

            confidence = min(
                1.0,
                pit_probability + (risk_metrics.std_dev / 10)
            )

            recommended_tyre = self._choose_best_tyre(laps_remaining)

            risk_level = "LOW" if risk_metrics.std_dev <= 2 else "MEDIUM" if risk_metrics.std_dev <= 4 else "HIGH"

            explanation = (
                f"Pit probability: {pit_probability:.2f} | "
                f"Tyre wear: {tyre_life}/{max_life} | "
                f"Position loss if PIT: {position_loss} | "
                f"Traffic: {position_prediction.traffic_risk} | "
                f"Risk spread: ±{risk_metrics.std_dev:.1f}s | "
                + ", ".join(explanation_parts)
            )

            return StrategyRecommendation(
                action=action,
                confidence=confidence,
                explanation=explanation,
                current_tyre=current_tyre,
                recommended_tyre=recommended_tyre,
                strategy_type=strategy_type,
                risk_level=risk_level
            )

        # --------------------------------------------------
        # RULE 1 — FINAL STINT
        # --------------------------------------------------
        if self._can_finish_race(current_tyre, tyre_life, laps_remaining):

            action = "STAY OUT"
            strategy_type = "EXTEND"
            explanation_parts.append("Final stint reachable")

        # --------------------------------------------------
        # RULE 2 — PIT COOLDOWN
        # --------------------------------------------------
        elif self._cooldown_active(current_lap):

            action = "STAY OUT"
            strategy_type = "DEFEND"
            explanation_parts.append("Pit cooldown active")

        # --------------------------------------------------
        # RULE 3 — VERY HIGH PIT SIGNAL
        # --------------------------------------------------
        elif pit_probability >= 0.85:

            action = "PIT NOW"
            strategy_type = "UNDERCUT"
            explanation_parts.append("Very high pit probability")

        # --------------------------------------------------
        # RULE 4 — POSITION LOSS CHECK
        # --------------------------------------------------
        elif position_loss >= 6:

            action = "STAY OUT"
            strategy_type = "OVERCUT"
            explanation_parts.append("Large position loss if pitting")

        # --------------------------------------------------
        # RULE 5 — TRAFFIC RISK CHECK
        # --------------------------------------------------
        elif position_prediction.traffic_risk == "HIGH":

            action = "STAY OUT"
            strategy_type = "DEFEND"
            explanation_parts.append("High traffic risk")

        # --------------------------------------------------
        # RULE 6 — STRATEGY PROFILE THRESHOLD
        # --------------------------------------------------
        elif pit_probability >= threshold:

            action = "PIT NOW"
            strategy_type = "UNDERCUT"
            explanation_parts.append("Strategy threshold met")

            self.last_pit_lap = current_lap

        else:

            action = "STAY OUT"
            strategy_type = "EXTEND"
            explanation_parts.append("Probability below threshold")

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------
        confidence = min(
            1.0,
            pit_probability + (risk_metrics.std_dev / 10)
        )

        # --------------------------------------------------
        # TYRE RECOMMENDATION
        # --------------------------------------------------
        recommended_tyre = self._choose_best_tyre(laps_remaining)

        # --------------------------------------------------
        # RISK LEVEL
        # --------------------------------------------------
        if risk_metrics.std_dev <= 2:
            risk_level = "LOW"
        elif risk_metrics.std_dev <= 4:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # --------------------------------------------------
        # EXPLANATION
        # --------------------------------------------------
        explanation = (
            f"Pit probability: {pit_probability:.2f} | "
            f"Position loss if PIT: {position_loss} | "
            f"Traffic: {position_prediction.traffic_risk} | "
            f"Risk spread: ±{risk_metrics.std_dev:.1f}s | "
            + ", ".join(explanation_parts)
        )

        return StrategyRecommendation(
            action=action,
            confidence=confidence,
            explanation=explanation,
            current_tyre=current_tyre,
            recommended_tyre=recommended_tyre,
            strategy_type=strategy_type,
            risk_level=risk_level
        )