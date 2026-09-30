from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.session import Base

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())