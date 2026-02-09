from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.settings import get_normalized_data_dir
from app.domain.analytics.returns import log_returns
from app.domain.analytics.volatility import rolling_std
from app.services.market_data.reader import NormalizedCsvReader

router = APIRouter(prefix="/api/v1")


class VolPointOut(BaseModel):
    timestamp_utc: datetime
    value: float


@router.get("/assets/{symbol}/volatility", response_model=list[VolPointOut])
def get_volatility(
    symbol: str,
    timeframe: str = Query(default="1h", min_length=1),
    window: int = Query(default=24, ge=2, le=1000),
    limit: int = Query(default=500, ge=2, le=5000),
):
    reader = NormalizedCsvReader(normalized_dir=get_normalized_data_dir())
    try:
        points = reader.read_close_series(symbol=symbol, timeframe=timeframe, limit=limit)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Normalized data not found for {symbol} {timeframe}",
        ) from None

    close_points = [(p.timestamp_utc, p.close) for p in points]
    returns_points = log_returns(close_points)
    values = [(r.timestamp_utc, r.value) for r in returns_points]
    vol_points = rolling_std(values=values, window=window)

    return [{"timestamp_utc": v.timestamp_utc, "value": v.value} for v in vol_points]
