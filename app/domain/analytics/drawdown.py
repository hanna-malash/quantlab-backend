from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DrawdownPoint:
    timestamp_utc: datetime
    value: float
    peak_close: float


def drawdown_series(close_points: Iterable[tuple[datetime, float]]) -> list[DrawdownPoint]:
    points = list(close_points)
    if len(points) == 0:
        return []

    result: list[DrawdownPoint] = []
    peak = points[0][1]

    for ts, close in points:
        if close > peak:
            peak = close

        if peak <= 0:
            dd = 0.0
        else:
            dd = (close / peak) - 1.0

        result.append(DrawdownPoint(timestamp_utc=ts, value=dd, peak_close=peak))

    return result
