from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.core.config import settings
from app.models.user import Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")



import json
from typing import List, Union

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
    if getattr(admin, 'status', None) == 'SUSPENDED':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Your account has been suspended by the Super Admin.\nPlease contact the administrator for access."
        )
    return admin

def require_permission(modules: Union[str, List[str]]):
    """
    Requires the current Admin to have at least one of the specified modules enabled.
    If the user is SUPER_ADMIN, they can access everything.
    """
    if isinstance(modules, str):
        modules = [modules]

    async def permission_checker(current_user: Admin = Depends(get_current_user)):
        if current_user.role == "SUPER_ADMIN":
            # However, Super Admin shouldn't directly manage operational data, 
            # but they have full override access in the backend logic, 
            # and frontend routes hide this. Or we can strictly forbid them from operational endpoints:
            # Let's just allow them to pass for API sake if they need to, or enforce strict role.
            # The prompt says: "Super Admin should not directly manage Buyers, Sellers... Super Admin's responsibility is only Admin Directory".
            # Thus, we should block Super Admin from operational endpoints!
            raise HTTPException(status_code=403, detail="Super Admins cannot perform operational actions.")
            
        admin_modules = json.loads(current_user.modules) if current_user.modules else {}
        for mod in modules:
            if admin_modules.get(mod) is True:
                return current_user
                
        raise HTTPException(status_code=403, detail="Insufficient module permissions")
    return permission_checker

async def require_super_admin(current_user: Admin = Depends(get_current_user)):
    if current_user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super admin required")
    return current_user
