"""
Entitlement Mapper (Phase 2)

Pure, rule-based logic that answers: "which benefit does this transaction
belong to?" Reads the ground-truth rules from data/benefits.json — the
rules themselves are never hardcoded here, only the matching logic.

No database session, no FastAPI dependency — this can be unit-tested and
called from anywhere (a router, a script, a notebook) without setup.
"""

import json
import os
from typing import Optional, TypedDict

BENEFITS_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "benefits.json"
)


class MatchedBenefit(TypedDict):
    name: str
    type: str  # "credit" | "visit" | "protection"
    limit: float
    value_per_use: Optional[float]
    value_percent_of_purchase: Optional[float]


def load_benefit_rules_for_card(card_name: str) -> list[dict]:
    """Reads benefits.json and returns the benefit rule list for the given card."""
    with open(BENEFITS_JSON_PATH) as benefits_file:
        all_cards_data = json.load(benefits_file)

    for card_entry in all_cards_data["cards"]:
        if card_entry["card"] == card_name:
            return card_entry["benefits"]

    raise ValueError(f"No benefit rules found for card '{card_name}'")


def map_transaction_to_benefit(
    card_name: str,
    category: str,
    merchant_name: str,
    location_type: Optional[str],
    amount: float,
) -> Optional[MatchedBenefit]:
    """
    Applies the card's benefit rules to a single transaction and returns
    the matched benefit, or None if the transaction doesn't qualify for
    any benefit on this card.

    Matching order matters: more specific rules (merchant_match) are
    checked before broader category-only rules.
    """
    benefit_rules = load_benefit_rules_for_card(card_name)

    for rule in benefit_rules:
        if not _category_matches(rule, category):
            continue

        if rule.get("merchant_match") and rule["merchant_match"] != merchant_name:
            continue

        if rule.get("location_type_match") and rule["location_type_match"] != location_type:
            continue

        if rule.get("min_amount") and amount < rule["min_amount"]:
            continue

        return MatchedBenefit(
            name=rule["name"],
            type=rule["type"],
            limit=rule["limit"],
            value_per_use=rule.get("value_per_use"),
            value_percent_of_purchase=rule.get("value_percent_of_purchase"),
        )

    return None


def _category_matches(rule: dict, transaction_category: str) -> bool:
    return rule.get("category_match") == transaction_category