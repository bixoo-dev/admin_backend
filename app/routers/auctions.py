from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.trade import Auction
from app.schemas.all import AuctionResponse, ActionResponse, DecisionRequest
from app.dependencies.auth import get_current_user, require_permission, require_super_admin, Admin

router = APIRouter(prefix="/admin/auctions", tags=["auctions"])

@router.get("", response_model=dict)
async def get_auctions(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    result = await db.execute(select(Auction))
    auctions = result.scalars().all()
    return {"auctions": [AuctionResponse.model_validate(a) for a in auctions]}

@router.post("/{id}/void", response_model=ActionResponse)
async def void_auction(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission('auctions:void'))):
    result = await db.execute(select(Auction).filter(Auction.id == id))
    auction = result.scalars().first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    auction.status = 'VOIDED'
    await db.commit()
    return {"success": True, "message": "Auction voided successfully"}
