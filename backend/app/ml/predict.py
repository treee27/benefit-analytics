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


# Neutral baseline for attribution: an "average" request. Each feature's
# contribution = score(actual) - score(actual with that feature reset to
# its baseline value). Model-agnostic, no extra dependencies.
_BASELINE = {
    "category": None,  # neutralized by averaging over all categories
    "days_since_last_benefit_use": 60,
    "prior_click_rate": 0.5,
    "amount": 150.0,
}

_LABELS = {
    "category": "transaction category",
    "days_since_last_benefit_use": "recency of last benefit use",
    "prior_click_rate": "prior click rate",
    "amount": "transaction amount",
}


def explain_engagement(features: dict, top_n: int = 3) -> list:
    """
    Returns the top_n feature contributions to this score, most
    influential first, e.g.:
      [{"feature": "prior click rate", "contribution": 0.31}, ...]
    Positive contribution = pushed the score up vs. an average request.
    """
    model = _load_model()
    if model is None:
        return []

    score = predict_engagement(features)
    contributions = []
    for key in ("days_since_last_benefit_use", "prior_click_rate", "amount"):
        neutral = dict(features)
        neutral[key] = _BASELINE[key]
        contributions.append((key, score - predict_engagement(neutral)))

    cat_scores = [
        predict_engagement({**features, "category": c}) for c in CATEGORIES
    ]
    contributions.append(("category", score - sum(cat_scores) / len(cat_scores)))

    contributions.sort(key=lambda kv: abs(kv[1]), reverse=True)
    return [
        {"feature": _LABELS[k], "contribution": round(v, 4)}
        for k, v in contributions[:top_n]
    ]
