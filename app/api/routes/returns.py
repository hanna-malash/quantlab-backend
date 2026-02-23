from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.settings import get_normalized_data_dir
from app.domain.analytics.returns import log_returns, simple_returns
from app.services.market_data.reader import NormalizedCsvReader

router = APIRouter()


class ReturnPointOut(BaseModel):
    timestamp_utc: datetime
    value: float


@router.get("/assets/{symbol}/returns", response_model=list[ReturnPointOut])
def get_returns(
    symbol: str,
    timeframe: str = Query(default="1h", min_length=1),
    type: str = Query(default="log", pattern="^(log|simple)$"),
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
    if type == "simple":
        ret_points = simple_returns(close_points)
    else:
        ret_points = log_returns(close_points)

    return [{"timestamp_utc": r.timestamp_utc, "value": r.value} for r in ret_points]
