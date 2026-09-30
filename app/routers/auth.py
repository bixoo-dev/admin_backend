from fastapi import APIRouter, Depends, HTTPException
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
    access_token = create_access_token(data={"sub": admin.id, "role": admin.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AdminResponse)
async def get_me(current_user: Admin = Depends(get_current_user)):
    return current_user
