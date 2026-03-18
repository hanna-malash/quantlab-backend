from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.core.settings import get_normalized_data_dir
from app.domain.analytics.drawdown import drawdown_series
from app.domain.analytics.returns import log_returns, simple_returns
from app.domain.analytics.risk import (
    downside_deviation,
    mean,
    sharpe_ratio,
    sortino_ratio,
    stddev,
)
from app.schemas.risk import RiskSummaryOut
from app.services.market_data.reader import NormalizedCsvReader

router = APIRouter(tags=["risk"])


@router.get("/assets/{symbol}/risk-summary", response_model=RiskSummaryOut)
def get_risk_summary(
    symbol: str,
    timeframe: Annotated[str, Query(min_length=1)] = "1d",
    type: Annotated[str, Query(pattern="^(log|simple)$")] = "log",
    limit: Annotated[int, Query(ge=2, le=5000)] = 365,
    risk_free_rate: float = 0.0,
    downside_target: float = 0.0,
):
    normalized_symbol = symbol.strip().upper()

    reader = NormalizedCsvReader(normalized_dir=get_normalized_data_dir())
    try:
        points = reader.read_close_series(
            symbol=normalized_symbol,
            timeframe=timeframe,
            limit=limit,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Normalized data not found for {normalized_symbol} {timeframe}",
        ) from None

    close_points = [(point.timestamp_utc, point.close) for point in points]
    returns_points = (
        simple_returns(close_points) if type == "simple" else log_returns(close_points)
    )
    returns_values = [point.value for point in returns_points]

    drawdowns = drawdown_series(close_points)
    max_drawdown = min((point.value for point in drawdowns), default=None)

    return {
        "symbol": normalized_symbol,
        "timeframe": timeframe,
        "limit": limit,
        "return_type": type,
        "risk_free_rate": risk_free_rate,
        "downside_target": downside_target,
        "observations": len(returns_values),
        "mean_return": mean(returns_values),
        "volatility": stddev(returns_values),
        "downside_volatility": downside_deviation(
            returns_values,
            target=downside_target,
        ),
        "sharpe_ratio": sharpe_ratio(
            returns_values,
            risk_free_rate=risk_free_rate,
        ),
        "sortino_ratio": sortino_ratio(
            returns_values,
            risk_free_rate=risk_free_rate,
            target=downside_target,
        ),
        "max_drawdown": max_drawdown,
    }
