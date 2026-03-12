from datetime import datetime

from pydantic import BaseModel


class AssetSummaryOut(BaseModel):
    symbol: str
    name: str
    asset_class: str
    currency: str
    available_timeframes: list[str]
    summary_timeframe: str
    summary_window: int
    last_timestamp_utc: datetime | None
    last_close: float | None
    return_30: float | None
    volatility_30: float | None
    max_drawdown: float | None


class AssetsOverviewOut(BaseModel):
    assets: list[AssetSummaryOut]
