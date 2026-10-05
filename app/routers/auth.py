from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.user import Admin
from app.schemas.all import Token, AdminResponse
from app.core.security import verify_password, create_access_token
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).filter(Admin.email == form_data.username))
    admin = result.scalars().first()
    if not admin or not verify_password(form_data.password, admin.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not admin.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if admin.status == 'SUSPENDED':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Your account has been suspended by the Super Admin.\nPlease contact the administrator for access."
        )
    access_token = create_access_token(data={"sub": admin.id, "role": admin.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AdminResponse)
async def get_me(current_user: Admin = Depends(get_current_user)):
    return current_user

from app.schemas.all import ChangePasswordRequest
from app.core.security import get_password_hash

@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest, 
    db: AsyncSession = Depends(get_db), 
    current_user: Admin = Depends(get_current_user)
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.password_hash = get_password_hash(data.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password updated successfully"}
