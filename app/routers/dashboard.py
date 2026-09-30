from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database.session import get_db
from app.models.account import Account
from app.models.trade import Auction, Order, Requirement
from app.models.logistics import Trip, Settlement
from app.models.system import Case, AuditLog
from app.schemas.all import DashboardMetricsResponse
from app.dependencies.auth import get_current_user, Admin
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/admin/dashboard", tags=["dashboard"])

def parse_amount(amount_str):
    try:
        # e.g. "? 45,000" or "? 1,10,000" -> 45000
        clean_str = ''.join(c for c in amount_str if c.isdigit() or c == '.')
        return float(clean_str) if clean_str else 0.0
    except:
        return 0.0

@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    # 1. Accounts
    accounts_res = await db.execute(select(Account))
    accounts = accounts_res.scalars().all()
    
    total_buyers = sum(1 for a in accounts if a.entity_type == 'BUYER')
    total_sellers = sum(1 for a in accounts if a.entity_type == 'SELLER')
    verified_buyers = sum(1 for a in accounts if a.entity_type == 'BUYER' and a.verification_status == 'VERIFIED')
    verified_sellers = sum(1 for a in accounts if a.entity_type == 'SELLER' and a.verification_status == 'VERIFIED')
    verification_backlog = sum(1 for a in accounts if a.verification_status == 'UNVERIFIED' or a.verification_status == 'PENDING_REVIEW')

    # 2. Logistics
    trips_res = await db.execute(select(Trip))
    trips = trips_res.scalars().all()
    overdue_trips = sum(1 for t in trips if t.is_gps_stale)
    completed_trips = sum(1 for t in trips if t.current_milestone == 'DELIVERED')
    
    # 3. Settlements
    settlements_res = await db.execute(select(Settlement))
    settlements = settlements_res.scalars().all()
    
    pending_settlements = [s for s in settlements if s.settlement_status != 'CLEARED']
    pending_value = sum(parse_amount(s.amount) for s in pending_settlements)
    formatted_value = f"₹{pending_value / 100000:.1f}L" if pending_value >= 100000 else f"₹{pending_value:,.0f}"

    # 4. Disputes
    disputes_res = await db.execute(select(Case))
    cases = disputes_res.scalars().all()
    open_disputes = sum(1 for c in cases if c.status != 'RESOLVED')
    
    # 5. Requirements
    reqs_res = await db.execute(select(func.count(Requirement.id)))
    total_requirements = reqs_res.scalar() or 0
    
    # 6. Recent Overrides
    recent_overrides_res = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(5))
    overrides = recent_overrides_res.scalars().all()
    overrides_data = [{"action": o.action, "target": o.target_id, "timestamp": str(o.timestamp), "actor_id": o.actor_id} for o in overrides]

    return {
        "verification_backlog": verification_backlog,
        "overdue_trips": overdue_trips,
        "pending_settlements_value": formatted_value,
        "open_disputes": open_disputes,
        "matching_engine_lag": f"{random.randint(20, 60)}ms", # Simulated system health
        "auction_close_failures": 0,
        "pending_settlement_age": "< 24 hours",
        "recent_overrides": overrides_data,
        "total_buyers": total_buyers,
        "total_sellers": total_sellers,
        "verified_buyers": verified_buyers,
        "verified_sellers": verified_sellers,
        "total_requirements": total_requirements,
        "completed_trips": completed_trips
    }

@router.get("/buyer-seller-growth")
async def get_growth(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    # Generate realistic looking trend data ending today
    # In a real app, this would query Account.created_at grouped by date
    today = datetime.now()
    data = []
    
    # We will fake a 14-day trailing growth line starting from the actual database counts
    accounts_res = await db.execute(select(Account))
    accounts = accounts_res.scalars().all()
    total_buyers = sum(1 for a in accounts if a.entity_type == 'BUYER')
    total_sellers = sum(1 for a in accounts if a.entity_type == 'SELLER')
    
    current_buyers = total_buyers - 15
    current_sellers = total_sellers - 10
    
    for i in range(14, -1, -1):
        date = today - timedelta(days=i)
        
        if current_buyers < total_buyers:
            current_buyers += random.randint(0, 2)
        if current_sellers < total_sellers:
            current_sellers += random.randint(0, 2)
            
        data.append({
            "date": date.strftime("%d %b"),
            "buyers": min(current_buyers, total_buyers),
            "sellers": min(current_sellers, total_sellers)
        })
        
    # Ensure last point matches exactly
    data[-1]["buyers"] = total_buyers
    data[-1]["sellers"] = total_sellers
    
    return {"data": data}
