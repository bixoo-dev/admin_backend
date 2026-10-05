from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.user import Admin
from app.models.system import AuditLog
from app.schemas.all import AdminResponse, AdminCreateRequest, AdminActionRequest, ActionResponse
from app.dependencies.auth import get_current_user, require_super_admin
import uuid, json, datetime

from app.core.security import get_password_hash

router = APIRouter(prefix="/admin/admins", tags=["admins"])

@router.get("", response_model=dict)
async def get_admins(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(Admin).order_by(Admin.created_at.desc()))
    admins = result.scalars().all()
    return {"admins": [AdminResponse.model_validate(a) for a in admins]}

@router.post("", response_model=dict)
async def create_admin(data: AdminCreateRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    new_id = f"ADM-{uuid.uuid4().hex[:4].upper()}"
    token = uuid.uuid4().hex[:8]
    invite_link = f"https://admin.bixoo.com/invite/tok_{token}_auth"
    
    new_admin = Admin(
        id=new_id,
        name=data.name,
        email=data.email,
        password_hash=get_password_hash(data.password),
        role="ADMIN",
        phone=data.phone,
        department=data.department,
        role_title=data.roleTitle,
        employee_id=data.employeeId,
        status="ONBOARDING",
        joined_date=datetime.datetime.utcnow(),
        last_active="Never",
        login_ip="Pending verification",
        two_factor_enabled=data.requireTwoFactor,
        onboarding_step="Step 1: Invitation Dispatched",
        invite_link=invite_link,
        invite_sent_at=datetime.datetime.utcnow(),
        modules=json.dumps(data.modules or {}),
        activity_summary=json.dumps([{"action": "Admin invited and onboarding link created by Super Admin", "time": "Just now"}]),
        notes=data.notes
    )
    db.add(new_admin)
    
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action="ONBOARD_INVITE",
        target_id=new_id,
        reason="Created onboarding admin account"
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(new_admin)
    return {"admin": AdminResponse.model_validate(new_admin)}

@router.post("/{id}/action", response_model=dict)
async def admin_action(id: str, action: AdminActionRequest, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(Admin).filter(Admin.id == id))
    admin = result.scalars().first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
        
    modules = json.loads(admin.modules) if admin.modules else {}
    activities = json.loads(admin.activity_summary) if admin.activity_summary else []
    
    if action.action == "TOGGLE_MODULE":
        new_status = action.forcedValue if action.forcedValue is not None else not modules.get(action.moduleId, False)
        modules[action.moduleId] = new_status
        admin.modules = json.dumps(modules)
        activities.insert(0, {"action": f"Super Admin {'granted' if new_status else 'revoked'} {action.moduleId} access", "time": "Just now"})
        audit_action = f"MODULE_TOGGLE_{action.moduleId.upper()}"
        
    elif action.action == "BATCH_MODULES":
        modules.update(action.modulesPreset or {})
        admin.modules = json.dumps(modules)
        activities.insert(0, {"action": f"Super Admin applied preset: {action.presetName}", "time": "Just now"})
        audit_action = "MODULE_BATCH_UPDATE"
        
    elif action.action == "UPDATE_STATUS":
        admin.status = action.status
        activities.insert(0, {"action": f"Super Admin set account status to {action.status}", "time": "Just now"})
        if action.status == "SUSPENDED":
            audit_action = "ADMIN_SUSPENDED"
        elif action.status == "ACTIVE":
            audit_action = "ADMIN_REACTIVATED"
        else:
            audit_action = f"STATUS_UPDATE_{action.status.upper()}"
        
    elif action.action == "RESEND_INVITE":
        token = uuid.uuid4().hex[:8]
        admin.invite_link = f"https://admin.bixoo.com/invite/tok_{token}_auth"
        admin.invite_sent_at = datetime.datetime.utcnow()
        activities.insert(0, {"action": "Super Admin re-dispatched invite link", "time": "Just now"})
        audit_action = "RESEND_INVITE"

    admin.activity_summary = json.dumps(activities[:5])
    
    audit = AuditLog(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        actor_id=current_user.id,
        action=audit_action,
        target_id=admin.id,
        reason=f"Action: {action.action}"
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(admin)
    return {"admin": AdminResponse.model_validate(admin)}

@router.delete("/{id}")
async def delete_admin(id: str, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(require_super_admin)):
    result = await db.execute(select(Admin).filter(Admin.id == id))
    admin = result.scalars().first()
    if admin:
        await db.delete(admin)
        await db.commit()
    return {"success": True}
