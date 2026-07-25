# API & Data Contract

Read this before writing code that depends on the other person's work.
If you need to change something here, message the team first — this file
is the source of truth both of you build against.

## Transaction fields (what the ML teammate can rely on existing)

Every transaction has:
- `id`: int
- `transaction_date`: date (YYYY-MM-DD)
- `merchant_name`: string (e.g. "Uber", "Starbucks", "Best Buy")
- `category`: string, one of `dining`, `transport`, `travel`, `electronics`
- `amount`: float
- `location_type`: string or null (e.g. `"airport"`, or null if not applicable)

A flat CSV export of this table (`data/transactions.csv`) will be available
after Phase 1 seed script runs — the ML teammate should build against the
CSV, not against a live Postgres connection.

## ML function signature (what backend expects to call)

The ML teammate owns `backend/app/ml/predict.py` and must expose:

```python
def predict_engagement(features: dict) -> float:
    """
    Returns a probability (0.0-1.0) that the user will act on a nudge
    if sent right now.
    """
```

Expected `features` dict keys (finalize together before training):
- `category`: str
- `days_since_last_benefit_use`: int
- `prior_click_rate`: float (0.0-1.0)
- `amount`: float

This function must have **no FastAPI dependency** — plain Python in,
plain float out — so it can be dropped into a router with one line.

## Backend endpoint that will call it

```
POST /api/predict-engagement
Body: { "category": str, "days_since_last_benefit_use": int, "prior_click_rate": float, "amount": float }
Response: { "engagement_score": float }
```

This endpoint exists from day one as a **hardcoded stub** returning `0.75`
so the nudge engine can be built and demoed without waiting on the real
model. Swap the stub body for `predict_engagement(features)` once it's ready.
