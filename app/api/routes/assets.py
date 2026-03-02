from fastapi import APIRouter

from app.services.market_data.assets_inventory import build_assets_inventory

router = APIRouter(tags=["assets"])


@router.get("/assets")
def list_assets() -> dict:
    assets = build_assets_inventory()
    return {"assets": assets}