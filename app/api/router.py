from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.prices import router as prices_router
from app.api.routes.returns import router as returns_router
from app.api.routes.volatility import router as volatility_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(prices_router)
router.include_router(returns_router)
router.include_router(volatility_router)
