import math
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class VolPoint:
    timestamp_utc: datetime
    value: float


def rolling_std(values: list[tuple[datetime, float]], window: int) -> list[VolPoint]:
    if window <= 1:
        return []
    if len(values) < window:
        return []

    out: list[VolPoint] = []
    for i in range(window - 1, len(values)):
        ts = values[i][0]
        slice_vals = [v for _, v in values[i - window + 1 : i + 1]]
        mean = sum(slice_vals) / float(window)
        var = 0.0
        for x in slice_vals:
            var += (x - mean) * (x - mean)
        var = var / float(window)
        out.append(VolPoint(timestamp_utc=ts, value=math.sqrt(var)))
    return out
