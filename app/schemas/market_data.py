from datetime import datetime

from pydantic import BaseModel, Field


class OhlcvBar(BaseModel):
    symbol: str = Field(min_length=1)
    timestamp_utc: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
