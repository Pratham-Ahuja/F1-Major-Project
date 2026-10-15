import pandas as pd


# =========================================================
# PHASE 13.2 — METRICS & EVALUATION
# =========================================================

def compute_pit_metrics(decision_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute pit decision performance metrics.
    """

    required_cols = ["AI_Decision", "Real_Pit"]

    for col in required_cols:
        if col not in decision_df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = decision_df.copy()

    df["AI_PIT"] = df["AI_Decision"] == "PIT"
    df["REAL_PIT"] = df["Real_Pit"] == True

    true_positive = ((df["AI_PIT"]) & (df["REAL_PIT"])).sum()
    false_positive = ((df["AI_PIT"]) & (~df["REAL_PIT"])).sum()
    false_negative = ((~df["AI_PIT"]) & (df["REAL_PIT"])).sum()

    precision = (
        true_positive / (true_positive + false_positive)
        if (true_positive + false_positive) > 0
        else 0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if (true_positive + false_negative) > 0
        else 0
    )

    summary = pd.DataFrame([{
        "TruePositive": true_positive,
        "FalsePositive": false_positive,
        "FalseNegative": false_negative,
        "Precision": round(precision, 3),
        "Recall": round(recall, 3)
    }])

    return summary


def strategy_distribution(decision_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze how often each strategy type was used.
    """

    if "AI_Strategy" not in decision_df.columns:
        raise ValueError("Missing AI_Strategy column")

    return (
        decision_df["AI_Strategy"]
        .value_counts()
        .reset_index()
        .rename(columns={
            "index": "StrategyType",
            "AI_Strategy": "Count"
        })
    )
