import math
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReturnPoint:
    timestamp_utc: datetime
    value: float


def simple_returns(points: list[tuple[datetime, float]]) -> list[ReturnPoint]:
    if len(points) < 2:
        return []
    out: list[ReturnPoint] = []
    prev_price = points[0][1]
    for i in range(1, len(points)):
        ts, price = points[i]
        if prev_price == 0:
            r = 0.0
        else:
            r = (price / prev_price) - 1.0
        out.append(ReturnPoint(timestamp_utc=ts, value=r))
        prev_price = price
    return out


def log_returns(points: list[tuple[datetime, float]]) -> list[ReturnPoint]:
    if len(points) < 2:
        return []
    out: list[ReturnPoint] = []
    prev_price = points[0][1]
    for i in range(1, len(points)):
        ts, price = points[i]
        if prev_price <= 0 or price <= 0:
            r = 0.0
        else:
            r = math.log(price / prev_price)
        out.append(ReturnPoint(timestamp_utc=ts, value=r))
        prev_price = price
    return out
