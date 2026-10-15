import os
import pandas as pd


# =========================================================
# PHASE 13.2 — DECISION LOGGING
# =========================================================

LOG_DIR = "outputs/research_logs"


def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def log_decisions(
    decision_df: pd.DataFrame,
    year: int,
    gp_name: str,
    driver_id: str,
    tag: str = "baseline"
) -> str:
    """
    Save AI vs real decision logs for later analysis.
    """

    ensure_log_dir()

    safe_gp = gp_name.replace(" ", "_")

    filename = (
        f"{year}_{safe_gp}_{driver_id}_decisions_{tag}.csv"
    )

    path = os.path.join(LOG_DIR, filename)
    decision_df.to_csv(path, index=False)

    print(f"[LOG SAVED] {path}")
    return path
