"""Offline uplift simulation — answers the brief's "measurable uplift" task.

Compares two nudge policies over the seeded transaction history:
  A) SEND-ALL : every rule-triggered candidate nudge is sent
  B) EV-FILTER: send only when engagement_score x unused_value >= threshold
                (the policy the live /api/nudges/decide endpoint uses)

Runs entirely offline: reads data/transactions.csv + model.joblib.
No Postgres, no server, no network. Nothing here touches the live app.

Run from backend/:  python -m app.ml.evaluate_uplift
"""
import csv
import datetime
from pathlib import Path

from .decision import EV_THRESHOLD_DOLLARS
from .features import TRANSACTIONS_CSV, build_features
from .predict import predict_engagement

# Simplified stand-in for the rule engine's unclaimed lookup so this stays
# DB-free: candidate nudge value per category, mirroring data/benefits.json
# limits (dining credit $120, Uber credit $200, lounge 4 x $45, protection
# 10% of purchase). Real per-card unclaimed values vary as benefits get
# consumed; using the full limits gives an upper-bound but policy-neutral
# comparison — both policies see identical candidates.
def candidate_nudge_value(row: dict) -> float | None:
    category = row["category"]
    amount = float(row["amount"])
    if category == "dining":
        return 120.0
    if category == "transport" and row["merchant_name"] == "Uber":
        return 200.0
    if category == "travel" and row.get("location_type") == "airport":
        return 45.0
    if category == "electronics" and amount >= 1000.0:
        return round(0.10 * amount, 2)
    return None


def main():
    with open(TRANSACTIONS_CSV, newline="", encoding="utf-8") as f:
        transactions = list(csv.DictReader(f))

    all_candidates = []
    for row in transactions:
        unused = candidate_nudge_value(row)
        if unused is None:
            continue  # no rule fires -> no nudge under either policy

        features = build_features(
            int(row["card_id"]), row["category"], float(row["amount"]),
            as_of=datetime.date.fromisoformat(row["transaction_date"]),
        )
        score = predict_engagement(features)
        all_candidates.append((row["card_id"], row["category"], score * unused))

    sent_all = len(all_candidates)
    value_all = sum(ev for _, _, ev in all_candidates)

    print(f"transactions replayed     : {len(transactions)}")
    print(f"rule-triggered candidates : {sent_all}")
    print(f"send-all baseline         : {sent_all} nudges, "
          f"${value_all:,.0f} expected reclaimed value, "
          f"${value_all/sent_all:,.2f} per nudge")
    print()
    print("EV threshold sweep (send only when score x unused $ >= threshold):")
    print(f"{'threshold':>10} {'nudges':>7} {'fewer':>7} {'value kept':>11} {'$/nudge':>9}")
    for threshold in (10, 25, 40, 50, 60, 75, 100):
        kept = [ev for _, _, ev in all_candidates if ev >= threshold]
        n, v = len(kept), sum(kept)
        if n == 0:
            continue
        print(f"{'$'+str(threshold):>10} {n:>7} "
              f"{100*(1-n/sent_all):>6.0f}% "
              f"{100*(v/value_all):>10.0f}% "
              f"${v/n:>8,.2f}")
    print()
    print("read: pick the row where 'fewer' is high while 'value kept' stays")
    print("high — that operating point cuts notification fatigue at minimal")
    print("cost in reclaimable value.")


if __name__ == "__main__":
    main()
