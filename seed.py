import asyncio
import json
import uuid
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.user import Admin
from app.models.account import Account, CatalogListing
from app.models.trade import Requirement, Order, Offer, Auction
from app.models.logistics import Trip, Settlement
from app.models.system import Case, Report, AuditLog
from app.database.session import Base
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with AsyncSessionLocal() as db:
        
        # Clear existing data
        await db.execute(AuditLog.__table__.delete())
        await db.execute(Report.__table__.delete())
        await db.execute(Case.__table__.delete())
        await db.execute(Settlement.__table__.delete())
        await db.execute(Trip.__table__.delete())
        await db.execute(Auction.__table__.delete())
        await db.execute(Offer.__table__.delete())
        await db.execute(Order.__table__.delete())
        await db.execute(Requirement.__table__.delete())
        await db.execute(CatalogListing.__table__.delete())
        await db.execute(Account.__table__.delete())
        await db.execute(Admin.__table__.delete())

        # Admins
        admins = [
            Admin(
                id='ADM-9021', name='Ops Lead', email='ops@bixoo.com', 
                password_hash='$2b$12$Oi.v5bTJQwn2amOIVrJTWuXpTeXryPegNPY6sVkYYo68vi.n0cf6G', role='SUPER_ADMIN', # password
                phone='+91 90000 00001', department='Operations', role_title='Lead', employee_id='BX-EMP-001',
                status='ACTIVE', two_factor_enabled=True, modules=json.dumps({"seller": True, "buyer": True, "transporter": True, "auctions": True, "settlements": True, "cases": True, "settings": True}),
                activity_summary='[]', notes='System generated super admin'
            ),
            Admin(
                id='ADM-8804', name='Verification Rep', email='admin@bixoo.com', 
                password_hash='$2b$12$Oi.v5bTJQwn2amOIVrJTWuXpTeXryPegNPY6sVkYYo68vi.n0cf6G', role='ADMIN', # password
                phone='+91 90000 00002', department='Verification', role_title='Rep', employee_id='BX-EMP-002',
                status='ACTIVE', two_factor_enabled=False, modules=json.dumps({"seller": True, "buyer": True}),
                activity_summary='[]', notes='System generated admin'
            )
        ]
        db.add_all(admins)
        await db.commit()

        # Accounts (Buyers, Sellers, and Transporters)
        accounts = [
            Account(id='USR-1022', entity_type='BUYER', business_name='AgriCorp India', contact_number='9876543210', email='procurement@agricorp.in', gstin='33AAAAA1234A1Z5', registration_number='CIN-U01100TN2018PTC12044', address='Survey No. 44/2, Agro Industrial Park, Coimbatore, TN', verification_status='VERIFIED'),
            Account(id='USR-3301', entity_type='BUYER', business_name='Global Mills', contact_number='9876543211', email='supplychain@globalmills.com', gstin='29BBBBB5678B1Z2', registration_number='CIN-U15310KA2015PLC08912', address='Plot 18, KIADB Industrial Area, Whitefield, Bengaluru, KA', verification_status='VERIFIED'),
            Account(id='USR-4410', entity_type='BUYER', business_name='Local Retailers', contact_number='9876543212', email='ops@localretailers.coop', gstin='33CCCCC9101C1Z8', registration_number='COOP-TN-CHE-2021-99', address='No. 89 Market Road, Koyambedu Wholesale Complex, Chennai, TN', verification_status='UNVERIFIED'),
            Account(id='USR-8821', entity_type='SELLER', business_name='Sunrise Farms', contact_number='9876543220', email='contact@sunrisefarms.in', gstin='33FFFFF4321F1Z3', registration_number='CIN-U01409TN2019PTC13098', address='SF No. 120, Thondamuthur Road, Pollachi, TN', verification_status='VERIFIED'),
            Account(id='USR-9044', entity_type='SELLER', business_name='Green Valley', contact_number='9876543221', email='sales@greenvalleyagro.com', gstin='29GGGGG8765G1Z1', registration_number='CIN-U01111KA2016PLC09123', address='Estate Sector 4, Hassan Agro SEZ, Hassan, KA', verification_status='VERIFIED'),
            Account(id='USR-7011', entity_type='SELLER', business_name='Industrial Copper', contact_number='9876543222', email='accounts@indcopper.co.in', gstin='33HHHHH9988H1Z7', registration_number='CIN-U27201TN2012PTC08541', address='SIDCO Industrial Estate, Guindy, Chennai, TN', verification_status='SUSPENDED'),
            Account(id='USR-7731', entity_type='SELLER', business_name='New Age Farming', contact_number='9876543223', email='info@newagefarming.org', gstin='27IIIII3456I1Z0', registration_number='CIN-U01400MH2022PTC37890', address='Agro Innovation Center, Baramati, Pune, MH', verification_status='UNVERIFIED'),
            Account(id='USR-5510', entity_type='TRANSPORTER', business_name='Veloce Logistics Fleet', contact_number='9876543230', email='dispatch@velocefleet.in', gstin='33KKKKK1122K1Z8', registration_number='TN-LOG-2024-88', address='Plot 45, SIPCOT Transport Hub, Coimbatore, TN', fleet_docs_status='ALL_DOCS_VERIFIED', verification_status='VERIFIED'),
            Account(id='USR-5520', entity_type='TRANSPORTER', business_name='Kaveri Logistics Services', contact_number='9876543231', email='operations@kaverilogistics.com', gstin='29LLLLL3344L1Z2', registration_number='KA-LOG-2023-14', address='No. 12 Outer Ring Road Transport Depot, Bengaluru, KA', fleet_docs_status='EPOD_COMPLIANT', verification_status='VERIFIED'),
            Account(id='USR-5530', entity_type='TRANSPORTER', business_name='SpeedWings Freight Corp', contact_number='9876543232', email='support@speedwings.co', gstin='27MMMMM5566M1Z5', registration_number='MH-LOG-2025-09', address='Warehouse Zone 3, Bhiwandi Logistics Park, Thane, MH', fleet_docs_status='PERMITS_PENDING', verification_status='UNVERIFIED'),
        ]
        db.add_all(accounts)
        await db.commit()

        # Requirements
        reqs = [
            Requirement(id='REQ-5091', buyer_id='USR-1022', product='Premium Robusta Coffee Beans', total_requested=5000, unit='KG', remaining_qty=1500, status='MATCHING', is_flagged=False),
            Requirement(id='REQ-5088', buyer_id='USR-4410', product='Grade-A Basmati Rice', total_requested=10000, unit='KG', remaining_qty=10000, status='PUBLISHED', is_flagged=True),
        ]
        db.add_all(reqs)
        await db.commit()

        # Orders
        orders = [
            Order(id='ORD-8801', buyer_id='USR-1022', seller_id='USR-8821', source_type='OFFER', source_ref='OFF-110', agreed_qty='2500 KG', total_value='?12,12,500', logistics_linked='TRIP-4901', status='LOGISTICS_PENDING'),
            Order(id='ORD-8991', buyer_id='USR-3301', seller_id='USR-8821', source_type='AUCTION', source_ref='AUC-1099', agreed_qty='500 MT', total_value='?1,12,500,000', logistics_linked=None, status='FULFILLED'),
            Order(id='ORD-8802', buyer_id='USR-1022', seller_id='USR-9044', source_type='OFFER', source_ref='OFF-112', agreed_qty='1000 KG', total_value='?1,82,500', logistics_linked='TRIP-4902', status='FULFILLED'),
        ]
        db.add_all(orders)
        await db.commit()

        # Offers
        offers = [
            Offer(id='OFF-110', requirement_id='REQ-5091', buyer_id='USR-1022', seller_id='USR-8821', offered_qty='2500', latest_price='185', status='ACCEPTED', linked_order_id='ORD-8801'),
            Offer(id='OFF-112', requirement_id='REQ-5091', buyer_id='USR-1022', seller_id='USR-9044', offered_qty='1000', latest_price='182.5', status='ACCEPTED', linked_order_id='ORD-8802'),
            Offer(id='OFF-115', requirement_id='REQ-5091', buyer_id='USR-1022', seller_id='USR-7731', offered_qty='1500', latest_price='190', status='NEGOTIATING', linked_order_id=None),
        ]
        db.add_all(offers)
        await db.commit()
        
        # Auctions
        auctions = [
            Auction(id='AUC-1099', seller_id='USR-8821', product='500 MT Wheat (Grade A)', status='CLOSED', winner_computed=True, winning_buyer_id='USR-3301', winning_amount='112500000', linked_order_id='ORD-8991', is_flagged=False),
            Auction(id='AUC-1102', seller_id='USR-9044', product='2000 Liters Sunflower Oil', status='LIVE', winner_computed=False, is_flagged=True),
        ]
        db.add_all(auctions)
        await db.commit()

        # Catalog Listings
        listings = [
            CatalogListing(id='LST-3021', seller_id='USR-8821', category='Agricultural Produce / Grains', product_name='Premium Basmati Rice (1000 MT)', unit_price='185.00', status='PUBLISHED', is_flagged=False),
            CatalogListing(id='LST-3099', seller_id='USR-7011', category='Industrial / Raw Materials', product_name='Unverified Grade Copper Wire', unit_price='1750.00', status='FLAGGED', is_flagged=True),
        ]
        db.add_all(listings)
        await db.commit()
        
        # Trips
        trips = [
            Trip(id='TRIP-4901', order_id='ORD-8802', transporter='Veloce Fleet (TN-04-AB-4029)', route='Coimbatore Hub -> Chennai Port', current_milestone='IN_TRANSIT', gps_last_seen='2 mins ago', is_gps_stale=False, consignee_proof_submitted=False),
            Trip(id='TRIP-4899', order_id='ORD-8991', transporter='Kaveri Logistics (KA-01-CD-8910)', route='Salem Depot -> Bengaluru Central', current_milestone='DELIVERED', gps_last_seen='45 mins ago', is_gps_stale=True, consignee_proof_submitted=True),
        ]
        db.add_all(trips)
        await db.commit()
        
        # Settlements
        settlements = [
            Settlement(id='SET-9901', trip_id='TRIP-4899', payee='Kaveri Logistics Fleet', amount='142500.00', proof_status='EPOD_VERIFIED', settlement_status='SETTLEMENT_DUE', bank_ref_masked='HDFC......9104'),
        ]
        db.add_all(settlements)
        await db.commit()
        
        # Cases
        cases = [
            Case(id='CAS-7001', type='DISPUTE_COMPLETION', linked_entity='TRIP-4899', reporter_id='USR-4410', status='INVESTIGATING', sla='24h', evidence_attached=True),
        ]
        db.add_all(cases)
        await db.commit()
        
        # Reports
        reports = [
            Report(id='REP-01', title='Settlement Reconciliation Ledger', description='Daily export', format='CSV'),
        ]
        db.add_all(reports)
        await db.commit()
        
        # Audit Logs
        logs = [
            AuditLog(id='EVT-9092', actor_id='ADM-9021', action='VOID_AUCTION', target_id='AUC-1099', reason='POLICY_VIOLATION', ip_address='192.168.1.104'),
            AuditLog(id='EVT-9091', actor_id='ADM-8804', action='RECONCILE_SETTLEMENT', target_id='SET-9901', reason='PAYOUT_RECONCILIATION', ip_address='10.0.0.45'),
        ]
        db.add_all(logs)

        await db.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
