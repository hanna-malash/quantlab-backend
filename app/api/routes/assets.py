from fastapi import APIRouter

from app.schemas.assets import AssetsOverviewOut
from app.services.market_data.assets_inventory import build_assets_inventory
from app.services.market_data.assets_summary import build_assets_overview

router = APIRouter(tags=["assets"])


@router.get("/assets")
def list_assets() -> dict:
    assets = build_assets_inventory()
    return {"assets": assets}


@router.get("/assets/overview", response_model=AssetsOverviewOut)
def assets_overview() -> dict:
    assets = build_assets_overview()
    return {"assets": assets}
