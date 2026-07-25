# Benefit Underutilization Analytics — Phase 0 Scaffold

## Run it

1. Start Postgres:
   ```
   docker compose up -d
   ```

2. Backend:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   uvicorn app.main:app --reload
   ```
   Visit http://localhost:8000/docs for the Swagger UI.
   Visit http://localhost:8000/api/health — should return `{"status": "ok"}`.

3. Tables are auto-created on startup (dev convenience — see `app/main.py`).

## What's here

- `data/benefits.json` — ground-truth benefit rules (Gold card). This is
  what the entitlement mapper (Phase 2) will read.
- `backend/app/models.py` — SQLAlchemy models: User, Card, Transaction,
  BenefitUsage.
- `backend/app/database.py` — async engine + session.
- `docs/api-contract.md` — **read this before starting ML work** — it's
  the fixed interface between backend and the model.

## Next step (Phase 1)

Seed script: `data/seed_transactions.py` (not yet built) — generates
~200 synthetic transactions across 5 users using Faker, inserts into
Postgres, and dumps a flat `data/transactions.csv` so the ML teammate
can start feature engineering without needing Postgres running.

## ML: engagement prediction (`backend/app/ml/`)

The rule engine proposes candidate nudges; the ML layer decides whether
each one is actually worth sending.

- `predict.py` — `predict_engagement(features) -> float`, the contract
  function (plain Python, no FastAPI/DB deps). Falls back to the 0.75
  stub value if `model.joblib` is missing, so the backend never breaks.
  Also `explain_engagement(features)` — top feature contributions to a
  score, for explainability (e.g. "prior click rate +0.20").
- `features.py` — `build_features(card_id, category, amount)` derives
  `days_since_last_benefit_use` and `prior_click_rate` from the card's
  real history in `data/transactions.csv`, so callers only need a
  card_id + transaction.
- `decision.py` — expected-value filter:
  `engagement_score x unused benefit $ >= $10` → send, else hold. This
  is the downstream ML filter the nudge engine's docstring anticipates.
- `train.py` — GradientBoosting classifier (test ROC-AUC ~0.72).
  Retrain with `python -m app.ml.train` from `backend/`.
- `POST /api/nudges/decide` — full pipeline demo: rules → features from
  real history → score + explanation → send/hold decision.

**Honest data note:** no real nudge-click log exists yet, so training
labels are *synthesized* from a documented behavioral rule, anchored to
real seeded transactions (category/amount pairs sampled from
`data/transactions.csv`). When real click logs exist, replace
`make_training_rows()` in `train.py` with a loader for them and retrain
— the feature schema, model, and API don't change.
