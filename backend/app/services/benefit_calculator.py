"""
Benefit Utilization Calculator (Phase 3)

Takes a user's real transactions from the database, runs each through the
Phase 2 entitlement mapper, and aggregates used vs. unused value per
benefit. This produces the headline number: total unclaimed dollar value.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Card, Transaction
from app.services.entitlement_mapper import load_benefit_rules_for_card, map_transaction_to_benefit


async def calculate_unclaimed_benefits(session: AsyncSession, user_id: int) -> dict:
    """
    Returns a breakdown of used/unused value per benefit for the given
    user's card, plus a grand total unclaimed dollar amount.
    """
    card = await _get_users_card(session, user_id)
    all_transactions = await _get_transactions_for_card(session, card.id)
    benefit_rules = load_benefit_rules_for_card(card.card_name)

    # Start every benefit at zero usage so unused ones still show up
    usage_by_benefit_name = {rule["name"]: _empty_usage_bucket(rule) for rule in benefit_rules}

    for transaction in all_transactions:
        matched_benefit = map_transaction_to_benefit(
            card_name=card.card_name,
            category=transaction.category,
            merchant_name=transaction.merchant_name,
            location_type=transaction.location_type,
            amount=transaction.amount,
        )
        if matched_benefit is None:
            continue

        bucket = usage_by_benefit_name[matched_benefit["name"]]
        _apply_transaction_to_bucket(bucket, matched_benefit, transaction.amount)

    benefit_breakdown = {
        benefit_name: _finalize_bucket(bucket) for benefit_name, bucket in usage_by_benefit_name.items()
    }
    total_unclaimed_value = round(
        sum(bucket["unused_value"] for bucket in benefit_breakdown.values()), 2
    )

    return {
        "card_name": card.card_name,
        "benefits": benefit_breakdown,
        "total_unclaimed_value": total_unclaimed_value,
    }


async def _get_users_card(session: AsyncSession, user_id: int) -> Card:
    result = await session.execute(select(Card).where(Card.user_id == user_id))
    card = result.scalars().first()
    if card is None:
        raise ValueError(f"No card found for user_id={user_id}")
    return card


async def _get_transactions_for_card(session: AsyncSession, card_id: int) -> list[Transaction]:
    result = await session.execute(select(Transaction).where(Transaction.card_id == card_id))
    return list(result.scalars().all())


def _empty_usage_bucket(rule: dict) -> dict:
    return {
        "type": rule["type"],
        "limit": rule["limit"],
        "value_per_use": rule.get("value_per_use"),
        "value_percent_of_purchase": rule.get("value_percent_of_purchase"),
        "dollars_used": 0.0,
        "visits_used": 0,
        "protection_potential_value": 0.0,
    }


def _apply_transaction_to_bucket(bucket: dict, matched_benefit: dict, transaction_amount: float) -> None:
    if bucket["type"] == "credit":
        bucket["dollars_used"] += transaction_amount

    elif bucket["type"] == "visit":
        bucket["visits_used"] += 1

    elif bucket["type"] == "protection":
        eligible_value = transaction_amount * bucket["value_percent_of_purchase"]
        bucket["protection_potential_value"] += eligible_value


def _finalize_bucket(bucket: dict) -> dict:
    if bucket["type"] == "credit":
        used = min(bucket["dollars_used"], bucket["limit"])
        unused_value = max(bucket["limit"] - used, 0)
        dollar_value_used = used
        dollar_value_limit = bucket["limit"]

    elif bucket["type"] == "visit":
        remaining_visits = max(bucket["limit"] - bucket["visits_used"], 0)
        unused_value = remaining_visits * bucket["value_per_use"]
        used = bucket["visits_used"]
        dollar_value_used = bucket["visits_used"] * bucket["value_per_use"]
        dollar_value_limit = bucket["limit"] * bucket["value_per_use"]

    elif bucket["type"] == "protection":
        unused_value = min(bucket["protection_potential_value"], bucket["limit"])
        used = 0  # no claim mechanism exists yet, so nothing is ever "used"
        dollar_value_used = 0
        dollar_value_limit = None  # not a fixed spending budget like credit/visit

    else:
        used = 0
        unused_value = 0
        dollar_value_used = 0
        dollar_value_limit = None

    return {
        "type": bucket["type"],
        "limit": bucket["limit"],
        "used": round(used, 2) if isinstance(used, float) else used,
        "unused_value": round(unused_value, 2),
        "dollar_value_used": round(dollar_value_used, 2),
        "dollar_value_limit": round(dollar_value_limit, 2) if dollar_value_limit is not None else None,
    }
