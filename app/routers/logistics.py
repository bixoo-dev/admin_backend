from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.logistics import Trip, Settlement
from app.models.system import AuditLog
from app.schemas.all import TripResponse, SettlementResponse, ActionResponse, DecisionRequest
from app.dependencies.auth import get_current_user, require_super_admin, require_permission, Admin
import uuid

router = APIRouter(prefix="/admin", tags=["logistics"])

@router.get("/trips", response_model=dict)
async def get_trips(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    result = await db.execute(select(Trip))
    trips = result.scalars().all()
    return {"trips": [TripResponse.model_validate(t) for t in trips]}

@router.post("/trips/{id}/intervention", response_model=ActionResponse)
async def force_trip_intervention(id: str, decision: DecisionRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(Trip).filter(Trip.id == id))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    # Example logic for force intervention
    trip.current_milestone = "INTERVENTION_REQUIRED"
    trip.is_gps_stale = True
    
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8]}",
        actor_id=current_user.id,
        action="TRIP_FORCE_INTERVENTION",
        target_id=trip.id,
        reason=decision.reasonCode or "MANUAL_OVERRIDE"
    )
    db.add(audit)
    
    await db.commit()
    return {"success": True, "message": "Trip intervention applied"}

@router.get("/settlements", response_model=dict)
async def get_settlements(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    result = await db.execute(select(Settlement))
    settlements = result.scalars().all()
    return {"settlements": [SettlementResponse.model_validate(s) for s in settlements]}

@router.post("/settlements/{id}/reconcile", response_model=ActionResponse)
async def reconcile_settlement(id: str, decision: DecisionRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission('settlements:reconcile'))):
    result = await db.execute(select(Settlement).filter(Settlement.id == id))
    settlement = result.scalars().first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
        
    settlement.settlement_status = "CLEARED"
    
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8]}",
        actor_id=current_user.id,
        action="SETTLEMENT_RECONCILED",
        target_id=settlement.id,
        reason=decision.reasonCode or "MANUAL_RECONCILIATION"
    )
    db.add(audit)
    
    await db.commit()
    return {"success": True, "message": "Settlement reconciled successfully"}
