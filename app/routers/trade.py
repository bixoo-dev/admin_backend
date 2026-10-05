from fastapi import APIRouter, Depends, HTTPException
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

# --- Requirements ---
@router.get("/requirements", response_model=dict)
async def get_requirements(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Requirement).options(selectinload(Requirement.offers)))
    requirements = result.scalars().all()
    res = []
    for r in requirements:
        req_data = RequirementResponse.model_validate(r).model_dump()
        req_data['offers'] = [
            {"offerId": o.id, "sellerId": o.seller_id, "offeredQty": float(o.offered_qty) if o.offered_qty else 0, "status": o.status, "linkedOrder": o.linked_order_id}
            for o in r.offers
        ]
        res.append(req_data)
    return {"requirements": res}

@router.get("/requirements/{id}", response_model=RequirementResponse)
async def get_requirement(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Requirement).filter(Requirement.id == id))
    req = result.scalar_one_or_none()
    if not req: raise HTTPException(status_code=404, detail="Not found")
    return RequirementResponse.model_validate(req)

@router.post("/requirements", response_model=RequirementResponse)
async def create_requirement(data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    req = Requirement(**data)
    req.id = f"REQ-{uuid.uuid4().hex[:4].upper()}"
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return RequirementResponse.model_validate(req)

@router.put("/requirements/{id}", response_model=RequirementResponse)
async def update_requirement(id: str, data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Requirement).filter(Requirement.id == id))
    req = result.scalar_one_or_none()
    if not req: raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.items(): setattr(req, k, v)
    await db.commit()
    await db.refresh(req)
    return RequirementResponse.model_validate(req)

@router.delete("/requirements/{id}")
async def delete_requirement(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Requirement).filter(Requirement.id == id))
    req = result.scalar_one_or_none()
    if req:
        await db.delete(req)
        await db.commit()
    return {"success": True}

class ActionPayload(BaseModel):
    actionType: str
    reasonCode: str = ""
    notes: str = ""

@router.post("/requirements/{id}/action")
async def action_requirement(id: str, payload: ActionPayload, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Requirement).filter(Requirement.id == id))
    req = result.scalar_one_or_none()
    if not req: raise HTTPException(status_code=404, detail="Requirement not found")
    if payload.actionType == 'PAUSE': req.status = 'PAUSED'
    elif payload.actionType == 'FORCE_CLOSE': req.status = 'CLOSED'
    audit = AuditLog(id=f"AUD-{uuid.uuid4().hex[:8].upper()}", actor_id=current_user.id, action=f"REQUIREMENT_{payload.actionType}", target_id=req.id, reason=payload.reasonCode or "STATUS_CHANGE")
    db.add(audit)
    await db.commit()
    return {"success": True}

# --- Orders ---
@router.get("/orders", response_model=dict)
async def get_orders(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    return {"orders": [OrderResponse.model_validate(o) for o in orders]}

@router.get("/orders/{id}", response_model=OrderResponse)
async def get_order(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Order).filter(Order.id == id))
    order = result.scalar_one_or_none()
    if not order: raise HTTPException(status_code=404, detail="Not found")
    return OrderResponse.model_validate(order)

@router.post("/orders", response_model=OrderResponse)
async def create_order(data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    order = Order(**data)
    order.id = f"ORD-{uuid.uuid4().hex[:4].upper()}"
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)

@router.put("/orders/{id}", response_model=OrderResponse)
async def update_order(id: str, data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Order).filter(Order.id == id))
    order = result.scalar_one_or_none()
    if not order: raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.items(): setattr(order, k, v)
    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)

@router.delete("/orders/{id}")
async def delete_order(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(Order).filter(Order.id == id))
    order = result.scalar_one_or_none()
    if order:
        await db.delete(order)
        await db.commit()
    return {"success": True}

# --- Catalog ---
@router.get("/catalog", response_model=dict)
async def get_catalog(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(CatalogListing))
    listings = result.scalars().all()
    return {"listings": [ListingResponse.model_validate(l) for l in listings]}

@router.get("/catalog/{id}", response_model=ListingResponse)
async def get_listing(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(CatalogListing).filter(CatalogListing.id == id))
    listing = result.scalar_one_or_none()
    if not listing: raise HTTPException(status_code=404, detail="Not found")
    return ListingResponse.model_validate(listing)

@router.post("/catalog", response_model=ListingResponse)
async def create_listing(data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    listing = CatalogListing(**data)
    listing.id = f"LST-{uuid.uuid4().hex[:4].upper()}"
    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    return ListingResponse.model_validate(listing)

@router.put("/catalog/{id}", response_model=ListingResponse)
async def update_listing(id: str, data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(CatalogListing).filter(CatalogListing.id == id))
    listing = result.scalar_one_or_none()
    if not listing: raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.items(): setattr(listing, k, v)
    await db.commit()
    await db.refresh(listing)
    return ListingResponse.model_validate(listing)

@router.delete("/catalog/{id}")
async def delete_listing(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))):
    result = await db.execute(select(CatalogListing).filter(CatalogListing.id == id))
    listing = result.scalar_one_or_none()
    if listing:
        await db.delete(listing)
        await db.commit()
    return {"success": True}
