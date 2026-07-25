import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    card_id: int
    transaction_date: datetime.date
    merchant_name: str
    category: str
    amount: float
    location_type: Optional[str] = None


class NudgeOut(BaseModel):
    nudge_type: str
    message: str
    unused_value: float


class PredictEngagementRequest(BaseModel):
    category: str
    days_since_last_benefit_use: int
    prior_click_rate: float
    amount: float