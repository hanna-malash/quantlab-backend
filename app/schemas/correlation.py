from pydantic import BaseModel, Field


class CorrelationRowOut(BaseModel):
    symbol: str
    values: list[float]


class CorrelationMatrixOut(BaseModel):
    symbols: list[str]
    timeframe: str = Field(min_length=1)
    limit: int
    observations: int
    rows: list[CorrelationRowOut]
