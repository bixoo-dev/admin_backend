from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.routers.auth import router as auth_router
from app.routers.accounts import router as accounts_router
from app.routers.auctions import router as auctions_router
from app.routers.dashboard import router as dashboard_router
from app.routers.trade import router as trade_router
from app.routers.logistics import router as logistics_router
from app.routers.system import router as system_router
from app.routers.admins import router as admins_router

app = FastAPI(title=settings.app_name)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(',')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1")
app.include_router(auctions_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(trade_router, prefix="/api/v1")
app.include_router(logistics_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(admins_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
