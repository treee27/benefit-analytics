"""
Quick manual check for the nudge engine — run before wiring it into the API.

Run from backend/ with venv active:
    python -m app.services.test_nudge_engine_manually
"""

from app.services.nudge_engine import evaluate_nudge_rules

fake_unclaimed_breakdown = {
    "benefits": {
        "Uber Credit": {"type": "credit", "limit": 200, "used": 150.0, "unused_value": 50.0},
        "Dining Credit": {"type": "credit", "limit": 120, "used": 40.0, "unused_value": 80.0},
        "Lounge": {"type": "visit", "limit": 4, "used": 1, "unused_value": 135.0},
        "Purchase Protection": {"type": "protection", "limit": 10000, "used": 0, "unused_value": 150.0},
    }
}

test_cases = [
    # (transaction, expected_nudge_type)
    ({"category": "dining", "amount": 18.0, "location_type": None}, "dining_credit"),
    ({"category": "transport", "amount": 42.0, "location_type": "airport"}, "lounge_reminder"),
    ({"category": "electronics", "amount": 1500.0, "location_type": None}, "purchase_protection"),
    ({"category": "electronics", "amount": 500.0, "location_type": None}, None),  # below threshold
    ({"category": "transport", "amount": 12.0, "location_type": None}, None),  # no rule matches
]

if __name__ == "__main__":
    passed_count = 0

    for transaction, expected_nudge_type in test_cases:
        nudge = evaluate_nudge_rules(transaction, fake_unclaimed_breakdown)
        actual_nudge_type = nudge["nudge_type"] if nudge else None

        result_symbol = "PASS" if actual_nudge_type == expected_nudge_type else "FAIL"
        if result_symbol == "PASS":
            passed_count += 1

        print(f"[{result_symbol}] {transaction} -> expected: {expected_nudge_type}, got: {actual_nudge_type}")

    print(f"\n{passed_count}/{len(test_cases)} checks passed")