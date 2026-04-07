from datetime import datetime

from pydantic import BaseModel, Field


class PortfolioAllocationIn(BaseModel):
    symbol: str = Field(min_length=1)
    weight: float = Field(gt=0)


class PortfolioAnalyticsIn(BaseModel):
    allocations: list[PortfolioAllocationIn] = Field(min_length=2)
    timeframe: str = Field(default="1d", min_length=1)
    limit: int = Field(default=365, ge=2, le=5000)
    base_value: float = Field(default=100.0, gt=0)
    return_type: str = Field(default="log", pattern="^(log|simple)$")


class PortfolioAllocationOut(BaseModel):
    symbol: str
    weight: float


class PortfolioPointOut(BaseModel):
    timestamp_utc: datetime
    value: float


class PortfolioSummaryOut(BaseModel):
    total_return: float | None
    volatility: float | None
    max_drawdown: float | None


class PortfolioAnalyticsOut(BaseModel):
    timeframe: str = Field(min_length=1)
    limit: int
    observations: int
    base_value: float
    return_type: str = Field(pattern="^(log|simple)$")
    allocations: list[PortfolioAllocationOut]
    series: list[PortfolioPointOut]
    summary: PortfolioSummaryOut
