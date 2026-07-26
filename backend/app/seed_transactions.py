"""
Generates synthetic transactions for demo/testing and for the ML teammate's
feature engineering (via the CSV export at the bottom).

Run from the backend/ directory with the venv active:
    python -m app.seed_transactions
"""

import asyncio
import csv
import datetime
import random

from faker import Faker

from app.database import AsyncSessionLocal, Base, engine
from app.models import Card, Transaction, User

fake = Faker()

CATEGORY_MERCHANTS = {
    "dining": ["Starbucks", "Chipotle", "Olive Garden", "Local Diner", "Pizza Place"],
    "transport": ["Uber", "Lyft", "City Metro"],
    "travel": ["Delta Airlines", "Hilton Hotel", "United Airlines"],
    "electronics": ["Best Buy", "Apple Store", "Amazon Electronics"],
}

CATEGORY_AMOUNT_RANGES = {
    "dining": (10, 35),
    "transport": (8, 40),
    "travel": (150, 900),
    "electronics": (100, 2000),
}

NUMBER_OF_USERS = 5

# Instead of drawing 40 transactions uniformly across 4 categories (which
# reliably blows past Dining/Uber/Lounge limits every time), each user gets
# a randomized COUNT per category. This naturally produces a mix of
# partially-used and fully-used benefits across the 5 users, instead of
# everyone saturating every credit every time.
CATEGORY_TRANSACTION_COUNT_RANGES = {
    "dining": (0, 6),  # 0-6 dining trips a year, $10-35 each -> $0-210 vs. $120 limit
    "transport": (0, 6),  # 0-6 Uber rides, $8-40 each -> $0-240 vs. $200 limit
    "travel": (0, 3),  # 0-3 flights/hotels a year (lounge triggers on airline ones)
    "electronics": (0, 2),  # 0-2 big purchases a year
}


# The very first user created becomes card_id=1, which is the hardcoded
# DEMO_USER_ID the React frontend always displays. Random data for this
# user is too risky for a live demo — it can land at either extreme (fully
# saturated, or entirely unused, as we saw). Instead this user gets a fixed,
# hand-picked transaction history that guarantees a good story every time:
# a mix of partially-used credits, one lounge visit used, and one big
# electronics purchase for Purchase Protection.
DEMO_USER_FIXED_CATEGORY_TRANSACTIONS = [
    # Dining: $58 of $120 used -> $62 unused
    ("dining", "Chipotle", 22.0, None),
    ("dining", "Starbucks", 18.0, None),
    ("dining", "Local Diner", 18.0, None),
    # Transport/Uber: $105 of $200 used -> $95 unused
    ("transport", "Uber", 40.0, None),
    ("transport", "Uber", 35.0, None),
    ("transport", "Lyft", 30.0, None),
    # Travel: 1 of 4 lounge visits used -> 3 remaining ($135 unused)
    ("travel", "Delta Airlines", 420.0, "airport"),
    # Electronics: one big purchase, triggers Purchase Protection
    ("electronics", "Best Buy", 1200.0, None),
]


def build_fixed_demo_transactions(card_id: int) -> list[dict]:
    demo_transactions = []

    for category, merchant_name, amount, location_type in DEMO_USER_FIXED_CATEGORY_TRANSACTIONS:
        demo_transactions.append(
            {
                "card_id": card_id,
                "transaction_date": fake.date_between(start_date="-180d", end_date="today"),
                "merchant_name": merchant_name,
                "category": category,
                "amount": amount,
                "location_type": location_type,
            }
        )

    return demo_transactions


def build_random_transaction(card_id: int, category: str) -> dict:
    merchant_name = random.choice(CATEGORY_MERCHANTS[category])
    amount_low, amount_high = CATEGORY_AMOUNT_RANGES[category]
    amount = round(random.uniform(amount_low, amount_high), 2)

    location_type = None
    if category == "travel" and "Airlines" in merchant_name:
        location_type = "airport"

    transaction_date = fake.date_between(start_date="-365d", end_date="today")

    return {
        "card_id": card_id,
        "transaction_date": transaction_date,
        "merchant_name": merchant_name,
        "category": category,
        "amount": amount,
        "location_type": location_type,
    }


def build_transactions_for_user(card_id: int) -> list[dict]:
    user_transactions = []

    for category, (minimum_count, maximum_count) in CATEGORY_TRANSACTION_COUNT_RANGES.items():
        transaction_count_for_category = random.randint(minimum_count, maximum_count)
        for _ in range(transaction_count_for_category):
            user_transactions.append(build_random_transaction(card_id, category))

    return user_transactions


async def seed_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    all_generated_transactions = []

    async with AsyncSessionLocal() as session:
        for user_index in range(NUMBER_OF_USERS):
            new_user = User(full_name=fake.name(), email=fake.unique.email())
            session.add(new_user)
            await session.flush()  # get new_user.id before creating the card

            new_card = Card(user_id=new_user.id, card_name="Gold")
            session.add(new_card)
            await session.flush()  # get new_card.id before creating transactions

            if user_index == 0:
                transactions_for_this_user = build_fixed_demo_transactions(new_card.id)
            else:
                transactions_for_this_user = build_transactions_for_user(new_card.id)

            for transaction_data in transactions_for_this_user:
                new_transaction = Transaction(**transaction_data)
                session.add(new_transaction)
                all_generated_transactions.append(transaction_data)

        await session.commit()

    write_transactions_csv(all_generated_transactions)
    print(
        f"Seeded {NUMBER_OF_USERS} users with a Gold card each and a randomized "
        f"transaction history per user. CSV exported to data/transactions.csv"
    )


def write_transactions_csv(transactions: list[dict]) -> None:
    csv_path = "../data/transactions.csv"
    fieldnames = ["card_id", "transaction_date", "merchant_name", "category", "amount", "location_type"]

    with open(csv_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in transactions:
            writer.writerow(row)


if __name__ == "__main__":
    asyncio.run(seed_database())
