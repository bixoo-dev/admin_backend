from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.system import Case, AuditLog
from app.schemas.all import CaseResponse, AuditLogResponse, ActionResponse, DecisionRequest
from app.dependencies.auth import get_current_user, require_super_admin, require_permission, Admin
import uuid

router = APIRouter(prefix="/admin", tags=["system"])

@router.get("/cases", response_model=dict)
async def get_cases(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    result = await db.execute(select(Case))
    cases = result.scalars().all()
    return {"cases": [CaseResponse.model_validate(c) for c in cases]}

@router.post("/cases/{id}/resolve", response_model=ActionResponse)
async def resolve_case(id: str, decision: DecisionRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_permission('cases:triage'))):
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

@router.get("/settings/audit-logs", response_model=dict)
async def get_audit_logs(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()))
    logs = result.scalars().all()
    return {"logs": [AuditLogResponse.model_validate(l) for l in logs]}
