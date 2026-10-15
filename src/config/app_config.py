from dataclasses import dataclass


# =========================================================
# STRATEGY PROFILE CONFIG
# =========================================================
@dataclass
class StrategyProfileConfig:
    name: str
    pit_threshold: float
    aggression_multiplier: float


# =========================================================
# SIMULATOR CONFIG
# =========================================================
@dataclass
class SimulatorConfig:
    base_lap_time: float = 90.0
    degradation_per_lap: float = 0.15
    pit_loss_seconds: float = 22.0


# =========================================================
# MONTE CARLO CONFIG
# =========================================================
@dataclass
class RiskConfig:
    volatility_scale: float = 1.0


# =========================================================
# MAIN APPLICATION CONFIG
# =========================================================
class AppConfig:

    def __init__(self, strategy_profile: str = "balanced"):

        # Core Config Sections
        self.simulator = SimulatorConfig()
        self.risk = RiskConfig()

        # Strategy Profile Selection
        self.strategy_profile = self._build_strategy_profile(
            strategy_profile.lower()
        )

    # -----------------------------------------------------
    # Strategy Profiles
    # -----------------------------------------------------
    def _build_strategy_profile(self, profile_name: str) -> StrategyProfileConfig:

        if profile_name == "aggressive":
            return StrategyProfileConfig(
                name="Aggressive",
                pit_threshold=0.55,
                aggression_multiplier=1.3
            )

        elif profile_name == "conservative":
            return StrategyProfileConfig(
                name="Conservative",
                pit_threshold=0.75,
                aggression_multiplier=0.8
            )

        else:
            # Default = Balanced
            return StrategyProfileConfig(
                name="Balanced",
                pit_threshold=0.65,
                aggression_multiplier=1.0
            )