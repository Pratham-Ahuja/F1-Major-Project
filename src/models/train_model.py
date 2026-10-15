import os
import pickle
import pandas as pd


# =========================================================
# Model Persistence Utilities (Production Safe)
# =========================================================

MODELS_DIR = "models_artifacts"
MODEL_FILENAME = "pit_model.pkl"


# ---------------------------------------------------------
# Directory handling
# ---------------------------------------------------------

def ensure_models_dir():
    """Create models directory if it does not exist."""
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)


# ---------------------------------------------------------
# VALIDATION UTILITIES
# ---------------------------------------------------------

def _validate_model(model):
    """
    Ensure loaded model is usable for inference.
    This prevents crashes during live race loop.
    """
    if model is None:
        raise ValueError("Loaded model is None")

    if not hasattr(model, "predict"):
        raise ValueError("Loaded object is not a valid ML model")

    if not hasattr(model, "predict_proba"):
        print("⚠️ WARNING: Model lacks predict_proba(). Fallback mode will be used.")

    return True


# ---------------------------------------------------------
# SAVE FUNCTIONS
# ---------------------------------------------------------

def save_model(model, model_name: str = "pit_model"):
    """
    Save a trained model to disk using pickle.
    """
    ensure_models_dir()

    path = os.path.join(MODELS_DIR, f"{model_name}.pkl")

    with open(path, "wb") as f:
        pickle.dump(model, f)

    print(f"Model saved → {path}")
    return path


def save_explainability(df: pd.DataFrame, name: str):
    """
    Save coefficients or feature importance DataFrame.
    """
    ensure_models_dir()

    path = os.path.join(MODELS_DIR, f"{name}.csv")
    df.to_csv(path, index=False)

    print(f"Explainability data saved → {path}")
    return path


# ---------------------------------------------------------
# LOAD FUNCTIONS
# ---------------------------------------------------------

def load_model(model_name: str = "pit_model"):
    """
    Load a saved model from disk safely.
    """

    ensure_models_dir()

    path = os.path.join(MODELS_DIR, f"{model_name}.pkl")

    # If model doesn't exist → signal training required
    if not os.path.exists(path):
        print("⚠️ No saved model found. Training required.")
        return None

    try:
        with open(path, "rb") as f:
            model = pickle.load(f)

        _validate_model(model)

        print("Model loaded successfully.")
        return model

    except Exception as e:
        print("⚠️ Model loading failed:", e)
        print("⚠️ Model will be retrained.")
        return None