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

# --- Trips ---
@router.get("/trips", response_model=dict)
async def get_trips(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['transporter', 'settlements']))):
    result = await db.execute(select(Trip))
    trips = result.scalars().all()
    return {"trips": [TripResponse.model_validate(t) for t in trips]}

@router.get("/trips/{id}", response_model=TripResponse)
async def get_trip(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['transporter', 'settlements']))):
    result = await db.execute(select(Trip).filter(Trip.id == id))
    trip = result.scalar_one_or_none()
    if not trip: raise HTTPException(status_code=404, detail="Not found")
    return TripResponse.model_validate(trip)

@router.post("/trips", response_model=TripResponse)
async def create_trip(data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['transporter', 'settlements']))):
    trip = Trip(**data)
    trip.id = f"TRP-{uuid.uuid4().hex[:4].upper()}"
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return TripResponse.model_validate(trip)

@router.put("/trips/{id}", response_model=TripResponse)
async def update_trip(id: str, data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['transporter', 'settlements']))):
    result = await db.execute(select(Trip).filter(Trip.id == id))
    trip = result.scalar_one_or_none()
    if not trip: raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.items(): setattr(trip, k, v)
    await db.commit()
    await db.refresh(trip)
    return TripResponse.model_validate(trip)

@router.delete("/trips/{id}")
async def delete_trip(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(Trip).filter(Trip.id == id))
    trip = result.scalar_one_or_none()
    if trip:
        await db.delete(trip)
        await db.commit()
    return {"success": True}

@router.post("/trips/{id}/intervention", response_model=ActionResponse)
async def force_trip_intervention(id: str, decision: DecisionRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(Trip).filter(Trip.id == id))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
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

# --- Settlements ---
@router.get("/settlements", response_model=dict)
async def get_settlements(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['transporter', 'settlements']))):
    result = await db.execute(select(Settlement))
    settlements = result.scalars().all()
    return {"settlements": [SettlementResponse.model_validate(s) for s in settlements]}

@router.get("/settlements/{id}", response_model=SettlementResponse)
async def get_settlement(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['transporter', 'settlements']))):
    result = await db.execute(select(Settlement).filter(Settlement.id == id))
    settlement = result.scalar_one_or_none()
    if not settlement: raise HTTPException(status_code=404, detail="Not found")
    return SettlementResponse.model_validate(settlement)

@router.post("/settlements", response_model=SettlementResponse)
async def create_settlement(data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['transporter', 'settlements']))):
    settlement = Settlement(**data)
    settlement.id = f"SET-{uuid.uuid4().hex[:4].upper()}"
    db.add(settlement)
    await db.commit()
    await db.refresh(settlement)
    return SettlementResponse.model_validate(settlement)

@router.put("/settlements/{id}", response_model=SettlementResponse)
async def update_settlement(id: str, data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['transporter', 'settlements']))):
    result = await db.execute(select(Settlement).filter(Settlement.id == id))
    settlement = result.scalar_one_or_none()
    if not settlement: raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.items(): setattr(settlement, k, v)
    await db.commit()
    await db.refresh(settlement)
    return SettlementResponse.model_validate(settlement)

@router.delete("/settlements/{id}")
async def delete_settlement(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(Settlement).filter(Settlement.id == id))
    settlement = result.scalar_one_or_none()
    if settlement:
        await db.delete(settlement)
        await db.commit()
    return {"success": True}

@router.post("/settlements/{id}/reconcile", response_model=ActionResponse)
async def reconcile_settlement(id: str, decision: DecisionRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['settlements']))):
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
