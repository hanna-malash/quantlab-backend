from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.settings import get_normalized_data_dir
from app.services.market_data.reader import NormalizedCsvReader

router = APIRouter(prefix="/api/v1")


class PricePointOut(BaseModel):
    timestamp_utc: datetime
    close: float


@router.get("/assets/{symbol}/prices", response_model=list[PricePointOut])
def get_prices(
    symbol: str,
    timeframe: str = Query(default="1h", min_length=1),
    limit: int = Query(default=500, ge=1, le=5000),
):
    reader = NormalizedCsvReader(normalized_dir=get_normalized_data_dir())
    try:
        points = reader.read_close_series(symbol=symbol, timeframe=timeframe, limit=limit)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Normalized data not found for {symbol} {timeframe}",
        ) from None
    return [{"timestamp_utc": p.timestamp_utc, "close": p.close} for p in points]
