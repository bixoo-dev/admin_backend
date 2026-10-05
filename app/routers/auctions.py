from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, desc
from app.database.session import get_db
from app.models.trade import Auction, Bid, Order
from app.models.system import AuditLog
from app.schemas.all import AuctionDetailResponse, ActionResponse, VoidLotRequest, BidResponse
from app.dependencies.auth import get_current_user, require_permission, require_super_admin, Admin
import uuid
import datetime

router = APIRouter(prefix="/admin/auctions", tags=["auctions"])

@router.get("", response_model=dict)
async def get_auctions(
    search: str = None, 
    status: str = None, 
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(require_permission(['auctions']))
):
    query = select(Auction).options(selectinload(Auction.bids)).order_by(desc(Auction.created_at))
    
    if search:
        query = query.filter(or_(
            Auction.id.ilike(f"%{search}%"),
            Auction.seller_id.ilike(f"%{search}%"),
            Auction.product.ilike(f"%{search}%")
        ))
    if status and status != 'ALL':
        query = query.filter(Auction.status == status)
        
    result = await db.execute(query)
    auctions = result.scalars().all()
    
    resp_auctions = []
    for a in auctions:
        resp = AuctionDetailResponse.model_validate(a)
        resp.bidCount = len(a.bids)
        if a.bids and a.status == 'LIVE':
            highest_bid = max(a.bids, key=lambda b: float(b.amount))
            resp.winningBid = {'amount': str(highest_bid.amount), 'buyerId': highest_bid.buyer_id}
        resp_auctions.append(resp)
        
    return {"auctions": resp_auctions}

@router.get("/{id}", response_model=AuctionDetailResponse)
async def get_auction(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['auctions']))):
    result = await db.execute(select(Auction).options(selectinload(Auction.bids)).filter(Auction.id == id))
    auction = result.scalar_one_or_none()
    if not auction: raise HTTPException(status_code=404, detail="Not found")
    
    resp = AuctionDetailResponse.model_validate(auction)
    resp.bidCount = len(auction.bids)
    if auction.bids and auction.status == 'LIVE':
        highest_bid = max(auction.bids, key=lambda b: float(b.amount))
        resp.winningBid = {'amount': str(highest_bid.amount), 'buyerId': highest_bid.buyer_id}
    resp.bids = [BidResponse.model_validate(b) for b in auction.bids]
    return resp

@router.get("/{id}/bids", response_model=dict)
async def get_auction_bids(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['auctions']))):
    result = await db.execute(select(Bid).filter(Bid.auction_id == id).order_by(desc(Bid.created_at)))
    bids = result.scalars().all()
    return {"bids": [BidResponse.model_validate(b) for b in bids]}

@router.post("/{id}/void", response_model=ActionResponse)
async def void_auction(id: str, data: VoidLotRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['auctions']))):
    result = await db.execute(select(Auction).filter(Auction.id == id))
    auction = result.scalars().first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
        
    if auction.status in ['VOIDED', 'CLOSED', 'CANCELLED']:
        raise HTTPException(status_code=400, detail=f"Cannot void auction in {auction.status} state")
    
    auction.status = 'VOIDED'
    
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action="VOID_AUCTION",
        target_id=id,
        reason=data.reason
    )
    db.add(audit)
    await db.commit()
    return {"success": True, "message": "Auction voided successfully"}

@router.post("/{id}/calculate-winner", response_model=dict)
async def calculate_winner(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['auctions']))):
    result = await db.execute(select(Auction).options(selectinload(Auction.bids)).filter(Auction.id == id))
    auction = result.scalar_one_or_none()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
        
    if auction.status != 'CLOSED':
        raise HTTPException(status_code=400, detail="Cannot calculate winner for non-closed auction")
        
    if auction.winner_computed:
        raise HTTPException(status_code=400, detail="Winner already computed")

    valid_bids = [b for b in auction.bids if b.status == 'ACCEPTED']
    
    if not valid_bids:
        auction.winner_computed = True
        auction.status = 'FAILED'
        await db.commit()
        return {"success": True, "message": "No valid bids found. Auction marked as FAILED."}
        
    # Find highest bid. In case of tie, earliest timestamp wins.
    highest_bid = sorted(valid_bids, key=lambda b: (-float(b.amount), b.created_at))[0]
    
    # Create an order
    order_id = f"ORD-{uuid.uuid4().hex[:4].upper()}"
    new_order = Order(
        id=order_id,
        buyer_id=highest_bid.buyer_id,
        seller_id=auction.seller_id,
        source_type='AUCTION',
        source_ref=auction.id,
        agreed_qty=auction.qty,
        total_value=str(highest_bid.amount),
        status='PENDING_SETTLEMENT'
    )
    db.add(new_order)
    
    auction.winner_computed = True
    auction.winning_buyer_id = highest_bid.buyer_id
    auction.winning_amount = str(highest_bid.amount)
    auction.winning_timestamp = highest_bid.created_at
    auction.linked_order_id = order_id
    
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action="CALCULATE_WINNER",
        target_id=id,
        reason=f"Winner calculated automatically"
    )
    db.add(audit)
    
    await db.commit()
    return {"success": True, "message": f"Winner computed successfully: {highest_bid.buyer_id}"}
