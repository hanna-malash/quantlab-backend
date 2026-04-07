from fastapi import APIRouter, HTTPException

from app.core.settings import get_normalized_data_dir
from app.domain.analytics.portfolio import (
    PortfolioAllocation,
    build_portfolio_series,
    normalize_allocations,
    portfolio_max_drawdown,
    portfolio_total_return,
    portfolio_volatility,
)
from app.schemas.portfolio import PortfolioAnalyticsIn, PortfolioAnalyticsOut
from app.services.market_data.reader import NormalizedCsvReader

router = APIRouter(tags=["portfolio"])


@router.post("/portfolio/analytics", response_model=PortfolioAnalyticsOut)
def get_portfolio_analytics(payload: PortfolioAnalyticsIn):
    try:
        allocations = normalize_allocations(
            [
                PortfolioAllocation(
                    symbol=allocation.symbol,
                    weight=allocation.weight,
                )
                for allocation in payload.allocations
            ]
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    reader = NormalizedCsvReader(normalized_dir=get_normalized_data_dir())

    prices_by_symbol: dict[str, list[tuple[object, float]]] = {}
    for allocation in allocations:
        try:
            points = reader.read_close_series(
                symbol=allocation.symbol,
                timeframe=payload.timeframe,
                limit=payload.limit,
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Normalized data not found for {allocation.symbol} {payload.timeframe}",
            ) from None

        prices_by_symbol[allocation.symbol] = [
            (point.timestamp_utc, point.close) for point in points
        ]

    try:
        series = build_portfolio_series(
            allocations=allocations,
            series_by_symbol=prices_by_symbol,
            base_value=payload.base_value,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return {
        "timeframe": payload.timeframe,
        "limit": payload.limit,
        "observations": len(series),
        "base_value": payload.base_value,
        "return_type": payload.return_type,
        "allocations": allocations,
        "series": series,
        "summary": {
            "total_return": portfolio_total_return(series),
            "volatility": portfolio_volatility(series, payload.return_type),
            "max_drawdown": portfolio_max_drawdown(series),
        },
    }
