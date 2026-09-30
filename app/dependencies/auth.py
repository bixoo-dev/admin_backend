from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.core.config import settings
from app.models.user import Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

ROLE_PERMISSIONS = {
  "ADMIN": [
    "accounts:verify",
    "catalog:review",
    "requirements:review",
    "trips:view",
    "cases:triage",
  ],
  "SUPER_ADMIN": [
    "accounts:verify",
    "accounts:suspend",
    "catalog:review",
    "catalog:override",
    "requirements:review",
    "requirements:override",
    "auctions:void",
    "orders:override",
    "trips:view",
    "trips:reassign",
    "settlements:reconcile",
    "comms:inspect",
    "settings:manage",
  ],
}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(Admin).filter(Admin.id == admin_id))
    admin = result.scalars().first()
    if admin is None:
        raise credentials_exception
    if not admin.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return admin

def require_permission(permission: str):
    async def permission_checker(current_user: Admin = Depends(get_current_user)):
        perms = ROLE_PERMISSIONS.get(current_user.role, [])
        if permission not in perms:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return permission_checker

async def require_super_admin(current_user: Admin = Depends(get_current_user)):
    if current_user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super admin required")
    return current_user
