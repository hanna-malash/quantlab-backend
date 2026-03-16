from datetime import datetime

from pydantic import BaseModel, Field


class NormalizedPerformancePointOut(BaseModel):
    timestamp_utc: datetime
    value: float


class NormalizedPerformanceSeriesOut(BaseModel):
    symbol: str
    points: list[NormalizedPerformancePointOut]


class NormalizedPerformanceOut(BaseModel):
    symbols: list[str]
    timeframe: str = Field(min_length=1)
    limit: int
    observations: int
    base_value: float
    series: list[NormalizedPerformanceSeriesOut]
