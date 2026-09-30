from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.database.session import get_db
from app.models.account import Account
from app.models.system import AuditLog
from app.schemas.all import AccountResponse, AccountCreate, AccountUpdate, DecisionRequest, ActionResponse
from app.dependencies.auth import get_current_user, require_permission, require_super_admin, Admin
import uuid

router = APIRouter(prefix="/admin/accounts", tags=["accounts"])

@router.get("", response_model=dict)
async def get_accounts(
    status: str = None, 
    search: str = None,
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(get_current_user)
):
    query = select(Account)
    
    if status and status.upper() != 'ALL':
        query = query.filter(Account.verification_status == status.upper())
        
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Account.id.ilike(search_pattern),
                Account.business_name.ilike(search_pattern),
                Account.gstin.ilike(search_pattern),
                Account.email.ilike(search_pattern),
                Account.contact_number.ilike(search_pattern)
            )
        )
        
    result = await db.execute(query)
    accounts = result.scalars().all()
    return {"accounts": [AccountResponse.model_validate(a) for a in accounts]}

@router.get("/{id}", response_model=AccountResponse)
async def get_account(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    result = await db.execute(select(Account).filter(Account.id == id))
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountResponse.model_validate(account)

@router.post("", response_model=AccountResponse)
async def create_account(account_in: AccountCreate, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission('accounts:verify'))):
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
async def update_account(id: str, account_in: AccountUpdate, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission('accounts:verify'))):
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
async def delete_account(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
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
async def submit_decision(id: str, decision: DecisionRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission('accounts:verify'))):
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
