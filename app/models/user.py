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
    phone = Column(String(50))
    department = Column(String(100))
    role_title = Column(String(100))
    employee_id = Column(String(50))
    status = Column(String(50), default='ACTIVE')
    joined_date = Column(DateTime)
    last_active = Column(String(100))
    login_ip = Column(String(50))
    two_factor_enabled = Column(Boolean, default=False)
    onboarding_step = Column(String(255))
    invite_link = Column(String(255))
    invite_sent_at = Column(DateTime)
    modules = Column(String(1000)) # We'll store JSON as string for simplicity with aiomysql or use JSON type
    activity_summary = Column(String(1000))
    notes = Column(String(1000))
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())