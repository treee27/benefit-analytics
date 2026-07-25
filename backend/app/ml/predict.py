"""Engagement prediction — plain Python in, plain float out.

Owned by the ML side, per docs/api-contract.md. No FastAPI dependency.
Loads the trained model (model.joblib, produced by train.py) lazily on
first call. If the artifact is missing, falls back to the contract's
0.75 stub value so the backend never breaks.
"""
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "model.joblib"
STUB_SCORE = 0.75

CATEGORIES = ["dining", "transport", "travel", "electronics"]

_model = None


def _load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        import joblib
        _model = joblib.load(MODEL_PATH)
    return _model


def _encode(features: dict) -> list:
    """category one-hot + numeric features. Order must match train.py."""
    row = [1.0 if features["category"] == c else 0.0 for c in CATEGORIES]
    row.append(float(features["days_since_last_benefit_use"]))
    row.append(float(features["prior_click_rate"]))
    row.append(float(features["amount"]))
    return row


def predict_engagement(features: dict) -> float:
    """
    Returns a probability (0.0-1.0) that the user will act on a nudge
    if sent right now.
    """
    model = _load_model()
    if model is None:
        return STUB_SCORE
    proba = model.predict_proba([_encode(features)])[0][1]
    return float(proba)
