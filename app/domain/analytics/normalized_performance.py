from dataclasses import dataclass
from datetime import datetime

from app.domain.analytics.correlation import align_series


@dataclass(frozen=True)
class NormalizedPerformancePoint:
    timestamp_utc: datetime
    value: float


@dataclass(frozen=True)
class NormalizedPerformanceSeries:
    symbol: str
    points: list[NormalizedPerformancePoint]


def align_price_series(
    series_by_symbol: dict[str, list[tuple[datetime, float]]],
) -> dict[str, list[float]]:
    return align_series(series_by_symbol)


def aligned_timestamps(
    series_by_symbol: dict[str, list[tuple[datetime, float]]],
) -> list[datetime]:
    if not series_by_symbol:
        return []

    timestamps_by_symbol = {
        symbol: {timestamp_utc for timestamp_utc, _ in points}
        for symbol, points in series_by_symbol.items()
    }
    common_timestamps = set.intersection(*timestamps_by_symbol.values())
    return sorted(common_timestamps)


def normalize_series(
    symbols: list[str],
    timestamps: list[datetime],
    aligned_prices: dict[str, list[float]],
    base_value: float,
) -> list[NormalizedPerformanceSeries]:
    series: list[NormalizedPerformanceSeries] = []

    for symbol in symbols:
        values = aligned_prices[symbol]
        if len(values) != len(timestamps):
            raise ValueError("aligned prices and timestamps must have equal lengths")
        if len(values) == 0:
            raise ValueError("cannot normalize an empty series")

        base_price = values[0]
        if base_price == 0:
            raise ValueError("cannot normalize a series with zero base price")

        points = [
            NormalizedPerformancePoint(
                timestamp_utc=timestamp,
                value=(price / base_price) * base_value,
            )
            for timestamp, price in zip(timestamps, values, strict=True)
        ]
        series.append(NormalizedPerformanceSeries(symbol=symbol, points=points))

    return series
