from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.schemas import PredictEngagementRequest, TransactionCreate
from app.services.benefit_calculator import calculate_unclaimed_benefits_by_card_id
from app.services.nudge_engine import evaluate_nudge_rules

router = APIRouter(prefix="/api", tags=["nudges"])


@router.post("/nudges/generate")
async def generate_nudge(payload: TransactionCreate, session: AsyncSession = Depends(get_db_session)):
    """
    Standalone nudge check — doesn't create a transaction, just evaluates
    what nudge (if any) a hypothetical transaction would trigger.
    """
    try:
        unclaimed_breakdown = await calculate_unclaimed_benefits_by_card_id(session, payload.card_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    triggered_nudge = evaluate_nudge_rules(payload.model_dump(), unclaimed_breakdown)
    return {"nudge": triggered_nudge}


@router.post("/predict-engagement")
def predict_engagement(payload: PredictEngagementRequest):
    """
    STUB — hardcoded until the ML teammate's real model lands in
    app/ml/predict.py. Swap the return line below for a call to
    predict_engagement(payload.model_dump()) once that exists.
    See docs/api-contract.md for the exact interface they're building to.
    """
    return {"engagement_score": 0.75}