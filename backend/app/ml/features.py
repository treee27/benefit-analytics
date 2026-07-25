"""Feature engineering from real transaction history.

Plain Python, no FastAPI/DB dependency — reads the flat CSV export
(data/transactions.csv) per the contract, so it runs anywhere.

Answers the open contract question of where `days_since_last_benefit_use`
and `prior_click_rate` come from at request time: the ML side derives
them from the card's transaction history.

Proxies (until real logs exist — documented, swap-in points marked):
  - "benefit use" proxy: a transaction that plausibly exercised a benefit
    (Uber ride, dining, airport travel, electronics >= $1000 — mirrors
    data/benefits.json). Real benefit-redemption logs would replace this.
  - prior_click_rate proxy: share of the card's transactions that were
    benefit-relevant — engaged cardmembers exercise benefits more. Real
    nudge-click logs would replace this.
"""
import csv
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TRANSACTIONS_CSV = REPO_ROOT / "data" / "transactions.csv"


def _is_benefit_use(row: dict) -> bool:
    category = row["category"]
    if category == "dining":
        return True
    if category == "transport" and row["merchant_name"] == "Uber":
        return True
    if category == "travel" and row.get("location_type") == "airport":
        return True
    if category == "electronics" and float(row["amount"]) >= 1000.0:
        return True
    return False


def _load_card_history(card_id: int) -> list:
    with open(TRANSACTIONS_CSV, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if int(r["card_id"]) == card_id]


def build_features(card_id: int, category: str, amount: float,
                   as_of: datetime.date | None = None) -> dict:
    """
    Returns the exact features dict predict_engagement() expects,
    derived from the card's real transaction history plus the incoming
    transaction's category/amount.
    """
    as_of = as_of or datetime.date.today()
    history = _load_card_history(card_id)

    benefit_dates = [
        datetime.date.fromisoformat(r["transaction_date"])
        for r in history if _is_benefit_use(r)
    ]
    if benefit_dates:
        days_since = max(0, (as_of - max(benefit_dates)).days)
    else:
        days_since = 120  # never used a benefit -> treat as maximally stale

    if history:
        click_rate = len(benefit_dates) / len(history)
    else:
        click_rate = 0.5  # unknown card -> neutral prior

    return {
        "category": category,
        "days_since_last_benefit_use": days_since,
        "prior_click_rate": round(click_rate, 3),
        "amount": float(amount),
    }
