import datetime

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True)

    cards: Mapped[list["Card"]] = relationship(back_populates="owner")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    card_name: Mapped[str] = mapped_column(String(60))  # e.g. "Gold"

    owner: Mapped["User"] = relationship(back_populates="cards")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="card")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    transaction_date: Mapped[datetime.date] = mapped_column(Date)
    merchant_name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(60))  # dining, transport, travel, electronics
    amount: Mapped[float] = mapped_column(Float)
    location_type: Mapped[str | None] = mapped_column(String(60), nullable=True)  # e.g. "airport"

    card: Mapped["Card"] = relationship(back_populates="transactions")
    benefit_usage_entries: Mapped[list["BenefitUsage"]] = relationship(back_populates="transaction")


class BenefitUsage(Base):
    """
    Records that a given transaction was mapped to a benefit and
    consumed some portion of that benefit's limit.
    """

    __tablename__ = "benefit_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    benefit_name: Mapped[str] = mapped_column(String(120))  # matches "name" in benefits.json
    amount_applied_to_benefit: Mapped[float] = mapped_column(Float)

    transaction: Mapped["Transaction"] = relationship(back_populates="benefit_usage_entries")
