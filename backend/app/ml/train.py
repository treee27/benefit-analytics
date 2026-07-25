"""Train the engagement model.

Run from the repo root:  python -m backend.app.ml.train
(or from backend/:       python -m app.ml.train)

Builds training rows anchored to the real data/transactions.csv — the
category/amount pairs are sampled from actual seeded transactions — and
synthesizes the behavioral features and click labels, since no click log
exists yet. The generative rule encodes the behavior we want the model
to learn for the demo:

  - habitual clickers keep clicking (prior_click_rate dominates)
  - a benefit used recently is fresher in mind (recency helps)
  - bigger-ticket categories/amounts make a nudge more compelling

When real nudge-click logs exist, replace make_training_rows() with a
loader for them; nothing else changes.

Writes model.joblib next to predict.py, which picks it up automatically.
"""
import math
import random
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from .predict import CATEGORIES, MODEL_PATH

REPO_ROOT = Path(__file__).resolve().parents[3]
TRANSACTIONS_CSV = REPO_ROOT / "data" / "transactions.csv"

CATEGORY_BOOST = {"travel": 0.9, "electronics": 0.6, "dining": 0.2, "transport": 0.0}


def make_training_rows(n=5000, seed=42):
    rng = random.Random(seed)
    tx = pd.read_csv(TRANSACTIONS_CSV)
    pairs = list(zip(tx["category"], tx["amount"]))

    rows = []
    for _ in range(n):
        category, amount = pairs[rng.randrange(len(pairs))]
        days = rng.randint(0, 120)
        prior = round(rng.random(), 3)
        logit = (
            -1.5
            + 3.0 * prior
            - 0.015 * days
            + CATEGORY_BOOST[category]
            + 0.0004 * amount
            + rng.gauss(0, 0.6)
        )
        p = 1 / (1 + math.exp(-logit))
        rows.append({
            "category": category,
            "days_since_last_benefit_use": days,
            "prior_click_rate": prior,
            "amount": amount,
            "clicked": int(rng.random() < p),
        })
    return pd.DataFrame(rows)


def build_matrix(df: pd.DataFrame):
    X = pd.DataFrame({f"cat_{c}": (df["category"] == c).astype(float) for c in CATEGORIES})
    X["days_since_last_benefit_use"] = df["days_since_last_benefit_use"].astype(float)
    X["prior_click_rate"] = df["prior_click_rate"].astype(float)
    X["amount"] = df["amount"].astype(float)
    return X.values


def main():
    if not TRANSACTIONS_CSV.exists():
        raise SystemExit(f"{TRANSACTIONS_CSV} not found — run the Phase 1 seed script first.")
    df = make_training_rows()
    X, y = build_matrix(df), df["clicked"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(f"test ROC-AUC: {auc:.3f}  ({len(df)} rows)")

    joblib.dump(model, MODEL_PATH)
    print(f"saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
