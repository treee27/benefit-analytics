from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import Transaction
from app.schemas import TransactionCreate
from app.services.benefit_calculator import calculate_unclaimed_benefits_by_card_id
from app.services.nudge_engine import evaluate_nudge_rules

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.post("")
async def create_transaction(payload: TransactionCreate, session: AsyncSession = Depends(get_db_session)):
    new_transaction = Transaction(**payload.model_dump())
    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)

    try:
        unclaimed_breakdown = await calculate_unclaimed_benefits_by_card_id(session, payload.card_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    triggered_nudge = evaluate_nudge_rules(payload.model_dump(), unclaimed_breakdown)

    return {
        "transaction_id": new_transaction.id,
        "nudge": triggered_nudge,
    }