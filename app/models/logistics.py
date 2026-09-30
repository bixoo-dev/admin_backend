from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base

class Trip(Base):
    __tablename__ = 'trips'
    id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.id'), nullable=False)
    transporter = Column(String(255))
    route = Column(String(255))
    current_milestone = Column(String(50))
    gps_last_seen = Column(String(100))
    is_gps_stale = Column(Boolean, default=False)
    consignee_proof_submitted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    order = relationship('Order')

class Settlement(Base):
    __tablename__ = 'settlements'
    id = Column(String(50), primary_key=True)
    trip_id = Column(String(50), ForeignKey('trips.id'), nullable=False)
    payee = Column(String(255))
    amount = Column(String(100))
    proof_status = Column(String(50))
    settlement_status = Column(String(50))
    bank_ref_masked = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    trip = relationship('Trip')