from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database.session import get_db
from app.models.trade import Requirement, Order, Offer
from app.models.account import CatalogListing
from app.models.system import AuditLog
from app.schemas.all import RequirementResponse, OrderResponse, ListingResponse
from app.dependencies.auth import get_current_user, require_permission, require_super_admin, Admin
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/admin", tags=["trade"])

@router.get("/requirements", response_model=dict)
async def get_requirements(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    result = await db.execute(select(Requirement).options(selectinload(Requirement.offers)))
    requirements = result.scalars().all()
    
    res = []
    for r in requirements:
        req_data = RequirementResponse.model_validate(r).model_dump()
        req_data['offers'] = [
            {
                "offerId": o.id,
                "sellerId": o.seller_id,
                "offeredQty": float(o.offered_qty) if o.offered_qty else 0,
                "status": o.status,
                "linkedOrder": o.linked_order_id
            }
            for o in r.offers
        ]
        res.append(req_data)
        
    return {"requirements": res}

class ActionPayload(BaseModel):
    actionType: str
    reasonCode: str = ""
    notes: str = ""

@router.post("/requirements/{id}/action")
async def action_requirement(id: str, payload: ActionPayload, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission("requirements:review"))):
    result = await db.execute(select(Requirement).filter(Requirement.id == id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    if payload.actionType == 'PAUSE':
        req.status = 'PAUSED'
    elif payload.actionType == 'FORCE_CLOSE':
        # Super admin check
        if current_user.role != 'SUPER_ADMIN':
            raise HTTPException(status_code=403, detail="Super Admin required to force close")
        req.status = 'CLOSED'
        
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action=f"REQUIREMENT_{payload.actionType}",
        target_id=req.id,
        reason=payload.reasonCode or "STATUS_CHANGE"
    )
    db.add(audit)
    
    await db.commit()
    return {"success": True}

@router.get("/orders", response_model=dict)
async def get_orders(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    return {"orders": [OrderResponse.model_validate(o) for o in orders]}

@router.get("/catalog", response_model=dict)
async def get_catalog(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    result = await db.execute(select(CatalogListing))
    listings = result.scalars().all()
    return {"listings": [ListingResponse.model_validate(l) for l in listings]}
