from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Numeric, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base

class Requirement(Base):
    __tablename__ = 'requirements'
    id = Column(String(50), primary_key=True)
    buyer_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    product = Column(String(255))
    total_requested = Column(Numeric(15,2))
    unit = Column(String(20))
    remaining_qty = Column(Numeric(15,2))
    deadline = Column(Date)
    status = Column(String(50))
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    buyer = relationship('Account', foreign_keys=[buyer_id])
    offers = relationship('Offer', back_populates='requirement')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(String(50), primary_key=True)
    buyer_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    seller_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    source_type = Column(String(50))
    source_ref = Column(String(50))
    agreed_qty = Column(String(100))
    total_value = Column(String(100))
    logistics_linked = Column(String(50))
    status = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    buyer = relationship('Account', foreign_keys=[buyer_id])
    seller = relationship('Account', foreign_keys=[seller_id])

class Offer(Base):
    __tablename__ = 'offers'
    id = Column(String(50), primary_key=True)
    requirement_id = Column(String(50), ForeignKey('requirements.id'), nullable=False)
    buyer_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    seller_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    offered_qty = Column(String(100))
    latest_price = Column(String(100))
    status = Column(String(50))
    history_count = Column(Integer, default=0)
    linked_order_id = Column(String(50), ForeignKey('orders.id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    requirement = relationship('Requirement', back_populates='offers')

class Auction(Base):
    __tablename__ = 'auctions'
    id = Column(String(50), primary_key=True)
    seller_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    product = Column(String(255))
    qty = Column(String(50))
    unit = Column(String(20))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String(50))
    winner_computed = Column(Boolean, default=False)
    winning_buyer_id = Column(String(50), ForeignKey('accounts.id'))
    winning_amount = Column(String(100))
    winning_timestamp = Column(DateTime, nullable=True)
    linked_order_id = Column(String(50), ForeignKey('orders.id'))
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    bids = relationship('Bid', back_populates='auction', order_by='desc(Bid.created_at)')

class Bid(Base):
    __tablename__ = 'bids'
    id = Column(String(50), primary_key=True)
    auction_id = Column(String(50), ForeignKey('auctions.id'), nullable=False)
    buyer_id = Column(String(50), ForeignKey('accounts.id'), nullable=False)
    amount = Column(Numeric(15,2), nullable=False)
    status = Column(String(50), default='ACCEPTED') # ACCEPTED, REJECTED, CANCELLED
    created_at = Column(DateTime, server_default=func.now())
    
    auction = relationship('Auction', back_populates='bids')