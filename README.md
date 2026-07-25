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
