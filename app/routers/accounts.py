import math
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from app.database.session import get_db
from app.models.account import Account
from app.models.system import AuditLog
from app.schemas.all import AccountResponse, AccountCreate, AccountUpdate, DecisionRequest, ActionResponse
from app.dependencies.auth import get_current_user, require_permission, require_super_admin, Admin

router = APIRouter(prefix="/admin/accounts", tags=["accounts"])

@router.get("", response_model=dict)
async def get_accounts(
    entity_type: Optional[str] = Query(None, description="Filter by entity type (BUYER, SELLER, TRANSPORTER, ALL)"),
    verification_status: Optional[str] = Query(None, description="Filter by verification status (VERIFIED, UNVERIFIED, PENDING)"),
    account_status: Optional[str] = Query(None, description="Filter by account status (ACTIVE, SUSPENDED)"),
    status: Optional[str] = Query(None, description="Legacy verification status filter"),
    search: Optional[str] = Query(None, description="Search by ID, business name, GSTIN, email, phone"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))
):
    """
    Unified Accounts query endpoint supporting filtering by:
    - Entity Type (BUYER, SELLER, TRANSPORTER)
    - Verification Status (VERIFIED, UNVERIFIED, PENDING)
    - Account Status (ACTIVE, SUSPENDED)
    - Search across ID, Business Name, Contact, Email, GSTIN
    - Configurable pagination
    """
    query = select(Account)
    
    # 1. Entity type filtering
    if entity_type and entity_type.upper() != 'ALL':
        query = query.filter(Account.entity_type == entity_type.upper())
        
    # 2. Verification status filtering
    ver_status = verification_status or status
    if ver_status and ver_status.upper() != 'ALL':
        query = query.filter(Account.verification_status == ver_status.upper())

    # 3. Account status filtering (ACTIVE vs SUSPENDED)
    if account_status and account_status.upper() != 'ALL':
        if account_status.upper() == 'SUSPENDED':
            query = query.filter(Account.verification_status == 'SUSPENDED')
        elif account_status.upper() == 'ACTIVE':
            query = query.filter(Account.verification_status != 'SUSPENDED')
        
    # 4. Search query filter
    if search and search.strip():
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Account.id.ilike(search_pattern),
                Account.business_name.ilike(search_pattern),
                Account.gstin.ilike(search_pattern),
                Account.email.ilike(search_pattern),
                Account.contact_number.ilike(search_pattern)
            )
        )
        
    # 5. Total count computation for pagination metadata
    count_subquery = query.subquery()
    count_query = select(func.count()).select_from(count_subquery)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one_or_none() or 0

    # 6. Apply pagination offset & limit
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    query = query.order_by(Account.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    accounts = result.scalars().all()
    
    return {
        "accounts": [AccountResponse.model_validate(a) for a in accounts],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("/{id}", response_model=AccountResponse)
async def get_account(
    id: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))
):
    result = await db.execute(select(Account).filter(Account.id == id))
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountResponse.model_validate(account)

@router.post("", response_model=AccountResponse)
async def create_account(
    account_in: AccountCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))
):
    new_account = Account(
        id=account_in.id,
        entity_type=account_in.entity_type,
        business_name=account_in.business_name,
        contact_number=account_in.contact_number,
        email=account_in.email,
        gstin=account_in.gstin,
        registration_number=account_in.registration_number,
        address=account_in.address,
        fleet_docs_status=account_in.fleet_docs_status,
        verification_status=account_in.verification_status
    )
    db.add(new_account)
    
    # Audit log
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action="CREATE_ACCOUNT",
        target_id=new_account.id,
        reason="MANUAL_CREATION"
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(new_account)
    return AccountResponse.model_validate(new_account)

@router.put("/{id}", response_model=AccountResponse)
async def update_account(
    id: str, 
    account_in: AccountUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))
):
    result = await db.execute(select(Account).filter(Account.id == id))
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = account_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
        
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action="UPDATE_ACCOUNT",
        target_id=account.id,
        reason="MANUAL_UPDATE"
    )
    db.add(audit)
        
    await db.commit()
    await db.refresh(account)
    return AccountResponse.model_validate(account)

@router.delete("/{id}", response_model=ActionResponse)
async def delete_account(
    id: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(require_super_admin)
):
    result = await db.execute(select(Account).filter(Account.id == id))
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    await db.delete(account)
    
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action="DELETE_ACCOUNT",
        target_id=id,
        reason="MANUAL_DELETION"
    )
    db.add(audit)
    
    await db.commit()
    return {"success": True, "message": "Account deleted"}

@router.post("/{id}/decisions", response_model=ActionResponse)
async def submit_decision(
    id: str, 
    decision: DecisionRequest, 
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(require_permission(['seller', 'buyer', 'transporter']))
):
    result = await db.execute(select(Account).filter(Account.id == id))
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if decision.actionType == 'VERIFY':
        account.verification_status = 'VERIFIED'
    elif decision.actionType == 'UNVERIFY':
        account.verification_status = 'UNVERIFIED'
    elif decision.actionType == 'SUSPEND':
        account.verification_status = 'SUSPENDED'
    elif decision.actionType == 'REACTIVATE':
        account.verification_status = 'VERIFIED'
        
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action=decision.actionType,
        target_id=account.id,
        reason=decision.reasonCode or "STATUS_CHANGE"
    )
    db.add(audit)
    
    await db.commit()
    return {"success": True, "message": "Decision applied"}
