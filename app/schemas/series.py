from datetime import datetime

from pydantic import BaseModel


class SeriesPointOut(BaseModel):
    timestamp_utc: datetime
    value: float


class PricePointOut(BaseModel):
    timestamp_utc: datetime
    close: float


class DrawdownPointOut(BaseModel):
    timestamp_utc: datetime
    value: float
    peak_close: float


class SeriesOut(BaseModel):
    symbol: str
    points: list[SeriesPointOut]


class PricesOut(BaseModel):
    symbol: str
    points: list[PricePointOut]


class DrawdownSeriesOut(BaseModel):
    symbol: str
    points: list[DrawdownPointOut]
