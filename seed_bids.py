import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.trade import Bid
from app.database.session import Base
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed_bids():
    async with AsyncSessionLocal() as db:
        await db.execute(Bid.__table__.delete())
        
        bids = [
            Bid(id='BID-001', auction_id='AUC-1099', buyer_id='USR-4410', amount=10500000, status='ACCEPTED'),
            Bid(id='BID-002', auction_id='AUC-1099', buyer_id='USR-3301', amount=11000000, status='ACCEPTED'),
            Bid(id='BID-003', auction_id='AUC-1099', buyer_id='USR-3301', amount=112500000, status='ACCEPTED'), # Winner
            
            Bid(id='BID-004', auction_id='AUC-1102', buyer_id='USR-1022', amount=50000, status='ACCEPTED'),
            Bid(id='BID-005', auction_id='AUC-1102', buyer_id='USR-7731', amount=55000, status='ACCEPTED'),
        ]
        
        db.add_all(bids)
        await db.commit()
        print("Bids seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_bids())
