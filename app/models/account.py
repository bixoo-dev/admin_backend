from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(String(50), primary_key=True)
    entity_type = Column(String(50), nullable=False)
    business_name = Column(String(255), nullable=False)
    contact_number = Column(String(50))
    email = Column(String(255))
    gstin = Column(String(50))
    registration_number = Column(String(100))
    address = Column(Text)
    fleet_docs_status = Column(String(50))
    verification_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    listings = relationship('CatalogListing', back_populates='seller')

class CatalogListing(Base):
    __tablename__ = 'catalog_listings'
    id = Column(String(50), primary_key=True)
    seller_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    category = Column(String(255))
    product_name = Column(String(255))
    unit_price = Column(String(50))
    status = Column(String(50))
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    seller = relationship('Account', back_populates='listings')
