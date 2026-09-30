from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base

class Case(Base):
    __tablename__ = 'cases'
    id = Column(String(50), primary_key=True)
    type = Column(String(50))
    linked_entity = Column(String(50))
    reporter_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    status = Column(String(50))
    sla = Column(String(50))
    evidence_attached = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    reporter = relationship('Account')

class Report(Base):
    __tablename__ = 'reports'
    id = Column(String(50), primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    last_run = Column(DateTime, nullable=True)
    format = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String(50), primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())
    actor_id = Column(String(50), ForeignKey('admins.id'), nullable=False)
    action = Column(String(100))
    target_id = Column(String(50))
    reason = Column(Text)
    ip_address = Column(String(50))
    case_ref = Column(String(50))
    actor = relationship('Admin')