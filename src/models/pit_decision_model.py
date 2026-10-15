import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


# =========================================================
# LABEL GENERATION (Explainable, shared across models)
# =========================================================

def generate_pit_labels(features_df: pd.DataFrame) -> pd.Series:
    """
    Generate explainable pit decision labels.

    PIT = 1 if:
    - LateStintFlag == True OR
    - TyreWeatherRiskScore >= 2
    Else:
    - STAY = 0
    """

    required_cols = ["LateStintFlag", "TyreWeatherRiskScore"]

    for col in required_cols:
        if col not in features_df.columns:
            raise ValueError(f"Missing required column: {col}")

    labels = (
        (features_df["LateStintFlag"] == True) |
        (features_df["TyreWeatherRiskScore"] >= 2)
    ).astype(int)

    return labels


# =========================================================
# INTERNAL FEATURE PREP (TRAIN + PREDICT SAFE)
# =========================================================

def _prepare_features(features_df: pd.DataFrame):

    X = features_df.select_dtypes(
        include=["int64", "float64", "bool"]
    ).copy()

    for col in ["LapNumber", "LapsRemaining"]:
        if col in X.columns:
            X.drop(columns=col, inplace=True)

    X = X.fillna(0)

    return X


# =========================================================
# FEATURE ALIGNMENT (FIXES TRAIN vs INFERENCE MISMATCH)
# =========================================================

def _align_features_with_model(model, X: pd.DataFrame):

    if not hasattr(model, "feature_names_in_"):
        return X

    expected_features = model.feature_names_in_

    for col in expected_features:
        if col not in X.columns:
            X[col] = 0

    X = X[expected_features]

    return X


# =========================================================
# BASELINE MODEL — LOGISTIC REGRESSION
# =========================================================

def train_baseline_model(features_df: pd.DataFrame):

    X = _prepare_features(features_df)

    y = generate_pit_labels(features_df)

    model = LogisticRegression(
        max_iter=1000,
        solver="lbfgs"
    )

    model.fit(X, y)

    coef_df = pd.DataFrame({
        "Feature": X.columns,
        "Coefficient": model.coef_[0]
    }).sort_values(by="Coefficient", ascending=False)

    return model, coef_df


def predict_pit_probability(model, features_df: pd.DataFrame) -> pd.Series:

    X = _prepare_features(features_df)

    X = _align_features_with_model(model, X)

    probs = model.predict_proba(X)[:, 1]

    return pd.Series(probs, index=features_df.index)


# =========================================================
# ADVANCED MODEL — RANDOM FOREST
# =========================================================

def train_advanced_model(features_df: pd.DataFrame):

    X = _prepare_features(features_df)

    y = generate_pit_labels(features_df)

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X, y)

    importance_df = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_
    }).sort_values(by="Importance", ascending=False)

    return model, importance_df


def predict_pit_probability_advanced(model, features_df: pd.DataFrame) -> pd.Series:

    X = _prepare_features(features_df)

    X = _align_features_with_model(model, X)

    probs = model.predict_proba(X)[:, 1]

    return pd.Series(probs, index=features_df.index)