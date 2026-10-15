from dataclasses import dataclass
import numpy as np
from src.simulation.strategy_simulator import SimulationResult


# =========================================================
# RISK METRICS OBJECT
# =========================================================
@dataclass
class RiskMetrics:
    mean_time: float
    best_case: float
    worst_case: float
    std_dev: float


# =========================================================
# MONTE CARLO SIMULATOR
# =========================================================
class MonteCarloSimulator:
    """
    Phase-9 stochastic simulator
    """

    def __init__(self, simulations: int = 200):
        self.simulations = simulations

    # -----------------------------------------------------
    # MAIN MONTE CARLO FUNCTION
    # -----------------------------------------------------
    def run(self, sim_result: SimulationResult) -> RiskMetrics:
        base_time = sim_result.estimated_remaining_time
        results = []

        for _ in range(self.simulations):
            noise = np.random.normal(0, 3.5)
            results.append(base_time + noise)

        results = np.array(results)

        return RiskMetrics(
            mean_time=float(results.mean()),
            best_case=float(results.min()),
            worst_case=float(results.max()),
            std_dev=float(results.std())
        )

    # -----------------------------------------------------
    # BACKWARD COMPATIBILITY FIX ⭐
    # -----------------------------------------------------
    # Old code was calling run_monte_carlo()
    def run_monte_carlo(self, sim_result: SimulationResult) -> RiskMetrics:
        return self.run(sim_result)