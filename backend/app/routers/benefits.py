from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.services.benefit_calculator import calculate_unclaimed_benefits
from app.services.dashboard_builder import build_dashboard_response

router = APIRouter(prefix="/api/users", tags=["benefits"])


@router.get("/{user_id}/unclaimed")
async def get_unclaimed_benefits(user_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        return await calculate_unclaimed_benefits(session, user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{user_id}/dashboard")
async def get_dashboard(user_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        unclaimed_breakdown = await calculate_unclaimed_benefits(session, user_id)
        return build_dashboard_response(unclaimed_breakdown)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))