from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.core.settings import get_normalized_data_dir
from app.domain.analytics.normalized_performance import (
    align_price_series,
    aligned_timestamps,
    normalize_series,
)
from app.schemas.compare import NormalizedPerformanceOut
from app.services.market_data.reader import NormalizedCsvReader

router = APIRouter(tags=["compare"])

DEFAULT_BASE_VALUE = 100.0


@router.get("/analytics/normalized-performance", response_model=NormalizedPerformanceOut)
def get_normalized_performance(
    symbols: Annotated[list[str], Query(min_length=2)],
    timeframe: Annotated[str, Query(min_length=1)] = "1d",
    limit: Annotated[int, Query(ge=2, le=5000)] = 365,
    base_value: Annotated[float, Query(gt=0)] = DEFAULT_BASE_VALUE,
):
    normalized_symbols = [symbol.strip().upper() for symbol in symbols if symbol.strip() != ""]
    deduped_symbols = list(dict.fromkeys(normalized_symbols))

    if len(deduped_symbols) < 2:
        raise HTTPException(status_code=422, detail="At least two unique symbols are required")

    reader = NormalizedCsvReader(normalized_dir=get_normalized_data_dir())

    prices_by_symbol: dict[str, list[tuple[object, float]]] = {}
    for symbol in deduped_symbols:
        try:
            points = reader.read_close_series(symbol=symbol, timeframe=timeframe, limit=limit)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Normalized data not found for {symbol} {timeframe}",
            ) from None

        prices_by_symbol[symbol] = [(point.timestamp_utc, point.close) for point in points]

    aligned_prices = align_price_series(prices_by_symbol)
    timestamps = aligned_timestamps(prices_by_symbol)
    observations = len(timestamps)

    if observations < 2:
        raise HTTPException(
            status_code=422,
            detail="Not enough overlapping observations to compute normalized performance",
        )

    try:
        series = normalize_series(deduped_symbols, timestamps, aligned_prices, base_value)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return {
        "symbols": deduped_symbols,
        "timeframe": timeframe,
        "limit": limit,
        "observations": observations,
        "base_value": base_value,
        "series": series,
    }
