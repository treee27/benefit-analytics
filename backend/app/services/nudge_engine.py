"""
Nudge Engine (Phase 5)

Pure, rule-based logic: given one incoming transaction and the current
unclaimed-benefit breakdown for that card, decide whether to fire a
nudge. No ML here — the ML teammate's engagement-score model (once it
exists) filters these candidate nudges downstream, it doesn't replace
this rule layer.
"""

from typing import Optional, TypedDict

DINING_UNUSED_THRESHOLD = 20.0
ELECTRONICS_AMOUNT_THRESHOLD = 1000.0


class Nudge(TypedDict):
    nudge_type: str
    message: str
    unused_value: float


def evaluate_nudge_rules(transaction: dict, unclaimed_breakdown: dict) -> Optional[Nudge]:
    """
    Checks the three brief-defined rules in priority order and returns
    the first one that fires, or None if nothing applies.
    """
    benefits = unclaimed_breakdown["benefits"]
    category = transaction.get("category")
    location_type = transaction.get("location_type")
    amount = transaction.get("amount", 0.0)

    dining_nudge = _check_dining_rule(category, benefits)
    if dining_nudge:
        return dining_nudge

    lounge_nudge = _check_airport_rule(location_type, benefits)
    if lounge_nudge:
        return lounge_nudge

    protection_nudge = _check_electronics_rule(category, amount, benefits)
    if protection_nudge:
        return protection_nudge

    return None


def _check_dining_rule(category: Optional[str], benefits: dict) -> Optional[Nudge]:
    if category != "dining":
        return None

    dining_info = benefits.get("Dining Credit")
    if dining_info is None or dining_info["unused_value"] <= DINING_UNUSED_THRESHOLD:
        return None

    return Nudge(
        nudge_type="dining_credit",
        message=f"You can save ${dining_info['unused_value']:.0f} today using your remaining Dining Credit.",
        unused_value=dining_info["unused_value"],
    )


def _check_airport_rule(location_type: Optional[str], benefits: dict) -> Optional[Nudge]:
    if location_type != "airport":
        return None

    lounge_info = benefits.get("Lounge")
    if lounge_info is None or lounge_info["unused_value"] <= 0:
        return None

    return Nudge(
        nudge_type="lounge_reminder",
        message=f"Use your lounge access today — worth ${lounge_info['unused_value']:.0f} remaining.",
        unused_value=lounge_info["unused_value"],
    )


def _check_electronics_rule(category: Optional[str], amount: float, benefits: dict) -> Optional[Nudge]:
    if category != "electronics" or amount <= ELECTRONICS_AMOUNT_THRESHOLD:
        return None

    protection_info = benefits.get("Purchase Protection")
    if protection_info is None or protection_info["unused_value"] <= 0:
        return None

    return Nudge(
        nudge_type="purchase_protection",
        message=(
            f"Your purchase may be eligible for Purchase Protection — "
            f"up to ${protection_info['unused_value']:.0f} in coverage."
        ),
        unused_value=protection_info["unused_value"],
    )