import pandas as pd
import numpy as np
from typing import Tuple


# =========================================================
# Inference Utilities (Model-Agnostic)
# =========================================================

def _prepare_numeric_features(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare numeric features consistently across all models.
    """

    if features_df is None or len(features_df) == 0:
        return pd.DataFrame()

    X = features_df.select_dtypes(
        include=["int64", "float64", "bool"]
    ).copy()

    # Remove non-informative columns
    for col in ["LapNumber", "LapsRemaining"]:
        if col in X.columns:
            X.drop(columns=col, inplace=True)

    return X.fillna(0)


def _align_model_features(model, X: pd.DataFrame) -> pd.DataFrame:
    """
    Align feature columns with model training schema.
    """

    if model is None:
        return X

    if hasattr(model, "feature_names_in_"):

        expected = list(model.feature_names_in_)

        # add missing columns
        for col in expected:
            if col not in X.columns:
                X[col] = 0

        # remove extra columns
        X = X[expected]

    return X


def run_inference(
    model,
    features_df: pd.DataFrame,
    threshold: float = 0.5
) -> Tuple[pd.Series, pd.Series]:
    """
    Run pit decision inference.

    ALWAYS returns safe output — never crashes the live loop.
    """

    # -----------------------------------------------------
    # Prepare features safely
    # -----------------------------------------------------

    X = _prepare_numeric_features(features_df)

    if X is None or X.empty:

        print("⚠️ Empty features received in inference. Using defaults.")

        safe_prob = pd.Series([0.05] * len(features_df), index=features_df.index)
        safe_decision = pd.Series([0] * len(features_df), index=features_df.index)

        return safe_prob, safe_decision

    # -----------------------------------------------------
    # Align with model schema
    # -----------------------------------------------------

    X = _align_model_features(model, X)

    # -----------------------------------------------------
    # CASE 0 — No model available
    # -----------------------------------------------------

    if model is None:

        print("⚠️ No ML model loaded. Using heuristic strategy.")

        # simple heuristic
        tyre_life = features_df.get("TyreLife", pd.Series([1]*len(features_df)))

        pit_prob = np.clip(tyre_life / 40, 0.05, 0.8)
        pit_decision = (pit_prob >= threshold).astype(int)

        return (
            pd.Series(pit_prob, index=features_df.index),
            pd.Series(pit_decision, index=features_df.index)
        )

    # -----------------------------------------------------
    # CASE 1 — Model supports probabilities
    # -----------------------------------------------------

    if hasattr(model, "predict_proba"):

        try:

            pit_prob = model.predict_proba(X)[:, 1]
            pit_decision = (pit_prob >= threshold).astype(int)

            return (
                pd.Series(pit_prob, index=features_df.index),
                pd.Series(pit_decision, index=features_df.index)
            )

        except Exception as e:

            print("⚠️ predict_proba failed → switching to fallback:", e)

    # -----------------------------------------------------
    # CASE 2 — Model supports only predict()
    # -----------------------------------------------------

    if hasattr(model, "predict"):

        try:

            preds = model.predict(X)

            pit_prob = np.where(preds == 1, 0.7, 0.1)
            pit_decision = preds.astype(int)

            print("⚠️ Using fallback probability conversion.")

            return (
                pd.Series(pit_prob, index=features_df.index),
                pd.Series(pit_decision, index=features_df.index)
            )

        except Exception as e:

            print("⚠️ predict() also failed:", e)

    # -----------------------------------------------------
    # CASE 3 — Ultimate fallback
    # -----------------------------------------------------

    print("⚠️ Model inference failed completely → using safe defaults.")

    safe_prob = pd.Series([0.05] * len(features_df), index=features_df.index)
    safe_decision = pd.Series([0] * len(features_df), index=features_df.index)

    return safe_prob, safe_decision


# =========================================================
# EXPLAINABILITY HELPER
# =========================================================

def explain_single_lap(
    features_df: pd.DataFrame,
    lap_index: int
) -> pd.DataFrame:

    if features_df is None or features_df.empty:
        raise ValueError("Features dataframe is empty")

    if lap_index not in features_df.index:
        raise ValueError("Invalid lap index")

    return features_df.loc[[lap_index]]