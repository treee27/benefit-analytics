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
    "dining": (10, 60),
    "transport": (8, 55),
    "travel": (150, 900),
    "electronics": (100, 2000),
}

NUMBER_OF_USERS = 5
TRANSACTIONS_PER_USER = 40


def build_random_transaction(card_id: int) -> dict:
    category = random.choice(list(CATEGORY_MERCHANTS.keys()))
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

            for _ in range(TRANSACTIONS_PER_USER):
                transaction_data = build_random_transaction(new_card.id)
                new_transaction = Transaction(**transaction_data)
                session.add(new_transaction)
                all_generated_transactions.append(transaction_data)

        await session.commit()

    write_transactions_csv(all_generated_transactions)
    print(
        f"Seeded {NUMBER_OF_USERS} users, each with a Gold card and "
        f"{TRANSACTIONS_PER_USER} transactions. CSV exported to data/transactions.csv"
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
