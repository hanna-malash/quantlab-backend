from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.settings import get_normalized_data_dir
from app.domain.analytics.drawdown import drawdown_series
from app.services.market_data.reader import NormalizedCsvReader

router = APIRouter()


class DrawdownPointOut(BaseModel):
    timestamp_utc: datetime
    value: float
    peak_close: float


@router.get("/assets/{symbol}/drawdown", response_model=list[DrawdownPointOut])
def get_drawdown(
    symbol: str,
    timeframe: str = Query(default="1d", min_length=1),
    limit: int = Query(default=500, ge=2, le=5000),
):
    normalized_symbol = symbol.strip().upper()

    reader = NormalizedCsvReader(normalized_dir=get_normalized_data_dir())
    try:
        points = reader.read_close_series(
            symbol=normalized_symbol, timeframe=timeframe, limit=limit
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Normalized data not found for {normalized_symbol} {timeframe}",
        ) from None

    close_points = [(p.timestamp_utc, p.close) for p in points]
    dd_points = drawdown_series(close_points)

    return [
        {"timestamp_utc": d.timestamp_utc, "value": d.value, "peak_close": d.peak_close}
        for d in dd_points
    ]
