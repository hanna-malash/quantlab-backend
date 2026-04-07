from dataclasses import dataclass
from datetime import datetime

from app.domain.analytics.drawdown import drawdown_series
from app.domain.analytics.normalized_performance import (
    align_price_series,
    aligned_timestamps,
)
from app.domain.analytics.returns import log_returns, simple_returns
from app.domain.analytics.risk import stddev


@dataclass(frozen=True)
class PortfolioAllocation:
    symbol: str
    weight: float


@dataclass(frozen=True)
class PortfolioPoint:
    timestamp_utc: datetime
    value: float


def normalize_allocations(
    allocations: list[PortfolioAllocation],
) -> list[PortfolioAllocation]:
    if len(allocations) < 2:
        raise ValueError("At least two portfolio allocations are required")

    deduped: dict[str, float] = {}
    for allocation in allocations:
        symbol = allocation.symbol.strip().upper()
        if symbol == "":
            continue
        deduped[symbol] = deduped.get(symbol, 0.0) + allocation.weight

    if len(deduped) < 2:
        raise ValueError("At least two unique portfolio symbols are required")

    total_weight = sum(weight for weight in deduped.values() if weight > 0)
    if total_weight <= 0:
        raise ValueError("Portfolio weights must sum to a positive value")

    normalized = [
        PortfolioAllocation(symbol=symbol, weight=weight / total_weight)
        for symbol, weight in deduped.items()
        if weight > 0
    ]

    if len(normalized) < 2:
        raise ValueError("At least two positive portfolio weights are required")

    return normalized


def build_portfolio_series(
    allocations: list[PortfolioAllocation],
    series_by_symbol: dict[str, list[tuple[datetime, float]]],
    base_value: float,
) -> list[PortfolioPoint]:
    timestamps = aligned_timestamps(series_by_symbol)
    if len(timestamps) < 2:
        raise ValueError("Not enough overlapping observations to compute portfolio analytics")

    aligned_prices = align_price_series(series_by_symbol)
    symbol_to_weight = {allocation.symbol: allocation.weight for allocation in allocations}

    base_prices: dict[str, float] = {}
    for symbol, values in aligned_prices.items():
        if len(values) != len(timestamps):
            raise ValueError("Aligned prices and timestamps must have equal lengths")
        if len(values) == 0:
            raise ValueError("Cannot build a portfolio from an empty aligned series")
        if values[0] == 0:
            raise ValueError(f"Cannot normalize a series with zero base price: {symbol}")
        base_prices[symbol] = values[0]

    points: list[PortfolioPoint] = []
    for index, timestamp in enumerate(timestamps):
        weighted_value = 0.0
        for symbol, values in aligned_prices.items():
            normalized_price = (values[index] / base_prices[symbol]) * base_value
            weighted_value += symbol_to_weight[symbol] * normalized_price
        points.append(PortfolioPoint(timestamp_utc=timestamp, value=weighted_value))

    return points


def portfolio_total_return(points: list[PortfolioPoint]) -> float | None:
    if len(points) < 2:
        return None

    start = points[0].value
    end = points[-1].value
    if start == 0:
        return None
    return (end / start) - 1.0


def portfolio_volatility(
    points: list[PortfolioPoint],
    return_type: str,
) -> float | None:
    close_points = [(point.timestamp_utc, point.value) for point in points]
    returns = simple_returns(close_points) if return_type == "simple" else log_returns(close_points)
    return stddev([point.value for point in returns])


def portfolio_max_drawdown(points: list[PortfolioPoint]) -> float | None:
    drawdowns = drawdown_series([(point.timestamp_utc, point.value) for point in points])
    return min((point.value for point in drawdowns), default=None)
