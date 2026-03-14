from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.core.settings import get_normalized_data_dir
from app.domain.analytics.correlation import align_series, correlation_matrix
from app.domain.analytics.returns import log_returns
from app.schemas.correlation import CorrelationMatrixOut
from app.services.market_data.reader import NormalizedCsvReader

router = APIRouter(tags=["correlation"])


@router.get("/analytics/correlation", response_model=CorrelationMatrixOut)
def get_correlation(
    symbols: Annotated[list[str], Query(min_length=2)],
    timeframe: Annotated[str, Query(min_length=1)] = "1d",
    limit: Annotated[int, Query(ge=2, le=5000)] = 365,
):
    normalized_symbols = [symbol.strip().upper() for symbol in symbols if symbol.strip() != ""]
    deduped_symbols = list(dict.fromkeys(normalized_symbols))

    if len(deduped_symbols) < 2:
        raise HTTPException(status_code=422, detail="At least two unique symbols are required")

    reader = NormalizedCsvReader(normalized_dir=get_normalized_data_dir())

    returns_by_symbol: dict[str, list[tuple[object, float]]] = {}
    for symbol in deduped_symbols:
        try:
            points = reader.read_close_series(symbol=symbol, timeframe=timeframe, limit=limit)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Normalized data not found for {symbol} {timeframe}",
            ) from None

        close_points = [(p.timestamp_utc, p.close) for p in points]
        returns_points = log_returns(close_points)
        returns_by_symbol[symbol] = [(point.timestamp_utc, point.value) for point in returns_points]

    aligned_returns = align_series(returns_by_symbol)
    observations = len(aligned_returns[deduped_symbols[0]])
    if observations < 2:
        raise HTTPException(
            status_code=422,
            detail="Not enough overlapping observations to compute correlation",
        )

    rows = correlation_matrix(deduped_symbols, aligned_returns)

    return {
        "symbols": deduped_symbols,
        "timeframe": timeframe,
        "limit": limit,
        "observations": observations,
        "rows": rows,
    }
