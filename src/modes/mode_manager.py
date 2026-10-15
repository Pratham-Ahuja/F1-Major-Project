from src.config.app_config import AppConfig
from src.modes.replay_mode import ReplayMode
from src.modes.research_mode import ResearchMode
from src.live_loop.race_loop import RaceLoop


class ModeManager:

    def __init__(
        self,
        mode: str,
        features_df,
        trained_model,
        total_laps: int,
        circuit_length_km: float,
        start_lap: int,
        end_lap: int,
        strategy_profile_name: str = "balanced"
    ):

        # Build global config
        self.config = AppConfig(strategy_profile=strategy_profile_name)

        self.mode = mode.lower()
        self.features_df = features_df
        self.model = trained_model
        self.total_laps = total_laps
        self.circuit_length_km = circuit_length_km
        self.start_lap = start_lap
        self.end_lap = end_lap

    # =====================================================
    # RUN SELECTED MODE
    # =====================================================
    def run(self):

        if self.mode == "live":

            race_loop = RaceLoop(
                features_df=self.features_df,
                trained_model=self.model,
                total_laps=self.total_laps,
                circuit_length_km=self.circuit_length_km,
                start_lap=self.start_lap,
                end_lap=self.end_lap,
                config=self.config
            )

            race_loop.run()

        elif self.mode == "replay":

            # Replay ignores start/end laps (full race replay)
            replay = ReplayMode(
                features_df=self.features_df,
                trained_model=self.model,
                total_laps=self.total_laps,
                circuit_length_km=self.circuit_length_km,
                config=self.config
            )

            replay.run()

        elif self.mode == "research":

            # Research respects start/end range
            research = ResearchMode(
                features_df=self.features_df,
                trained_model=self.model,
                total_laps=self.total_laps,
                circuit_length_km=self.circuit_length_km,
                start_lap=self.start_lap,
                end_lap=self.end_lap,
                config=self.config
            )

            research.run()

        else:
            print("\nInvalid mode selected. Please choose live / replay / research.\n")