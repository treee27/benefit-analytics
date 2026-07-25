"""
Quick manual check for the entitlement mapper — not a formal test suite,
just a fast way to confirm the rules behave as expected before wiring
this into the API.

Run from backend/ with venv active:
    python -m app.services.test_entitlement_mapper_manually
"""

from app.services.entitlement_mapper import map_transaction_to_benefit

sample_transactions = [
    # (category, merchant_name, location_type, amount) -> expected benefit name
    ("transport", "Uber", None, 42.0, "Uber Credit"),
    ("dining", "Chipotle", None, 18.0, "Dining Credit"),
    ("travel", "Delta Airlines", "airport", 420.0, "Lounge"),
    ("electronics", "Best Buy", None, 1500.0, "Purchase Protection"),
    ("electronics", "Best Buy", None, 950.0, None),  # below the $1000 min_amount, should not match
    ("dining", "Starbucks", None, 8.0, "Dining Credit"),
]

if __name__ == "__main__":
    passed_count = 0

    for category, merchant_name, location_type, amount, expected_benefit_name in sample_transactions:
        matched_benefit = map_transaction_to_benefit(
            card_name="Gold",
            category=category,
            merchant_name=merchant_name,
            location_type=location_type,
            amount=amount,
        )
        actual_benefit_name = matched_benefit["name"] if matched_benefit else None

        result_symbol = "PASS" if actual_benefit_name == expected_benefit_name else "FAIL"
        if result_symbol == "PASS":
            passed_count += 1

        print(
            f"[{result_symbol}] {merchant_name} (${amount}, {category}) "
            f"-> expected: {expected_benefit_name}, got: {actual_benefit_name}"
        )

    print(f"\n{passed_count}/{len(sample_transactions)} checks passed")