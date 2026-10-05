from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.system import Case, AuditLog
from app.schemas.all import CaseResponse, AuditLogResponse, ActionResponse, DecisionRequest
from app.dependencies.auth import get_current_user, require_super_admin, require_permission, Admin
import uuid

router = APIRouter(prefix="/admin", tags=["system"])

# --- Cases ---
@router.get("/cases", response_model=dict)
async def get_cases(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['cases', 'settings']))):
    result = await db.execute(select(Case))
    cases = result.scalars().all()
    return {"cases": [CaseResponse.model_validate(c) for c in cases]}

@router.get("/cases/{id}", response_model=CaseResponse)
async def get_case(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['cases', 'settings']))):
    result = await db.execute(select(Case).filter(Case.id == id))
    case_obj = result.scalar_one_or_none()
    if not case_obj: raise HTTPException(status_code=404, detail="Not found")
    return CaseResponse.model_validate(case_obj)

@router.post("/cases", response_model=CaseResponse)
async def create_case(data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['cases', 'settings']))):
    case_obj = Case(**data)
    case_obj.id = f"CAS-{uuid.uuid4().hex[:4].upper()}"
    db.add(case_obj)
    await db.commit()
    await db.refresh(case_obj)
    return CaseResponse.model_validate(case_obj)

@router.put("/cases/{id}", response_model=CaseResponse)
async def update_case(id: str, data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['cases', 'settings']))):
    result = await db.execute(select(Case).filter(Case.id == id))
    case_obj = result.scalar_one_or_none()
    if not case_obj: raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.items(): setattr(case_obj, k, v)
    await db.commit()
    await db.refresh(case_obj)
    return CaseResponse.model_validate(case_obj)

@router.delete("/cases/{id}")
async def delete_case(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(Case).filter(Case.id == id))
    case_obj = result.scalar_one_or_none()
    if case_obj:
        await db.delete(case_obj)
        await db.commit()
    return {"success": True}

@router.post("/cases/{id}/resolve", response_model=ActionResponse)
async def resolve_case(id: str, decision: DecisionRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission(['cases', 'settings']))):
    result = await db.execute(select(Case).filter(Case.id == id))
    case_obj = result.scalars().first()
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
        
    case_obj.status = "RESOLVED"
    
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8]}",
        actor_id=current_user.id,
        action="CASE_RESOLVED",
        target_id=case_obj.id,
        reason=decision.reasonCode or "MANUAL_RESOLUTION"
    )
    db.add(audit)
    
    await db.commit()
    return {"success": True, "message": "Case resolved"}

import json

@router.get("/settings/audit-logs", response_model=dict)
async def get_audit_logs(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    if current_user.role != "SUPER_ADMIN":
        admin_modules = json.loads(current_user.modules) if current_user.modules else {}
        if not admin_modules.get('settings'):
            raise HTTPException(status_code=403, detail="Insufficient module permissions")
            
    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()))
    logs = result.scalars().all()
    return {"logs": [AuditLogResponse.model_validate(l) for l in logs]}
