from pydantic import BaseModel, Field


class RiskSummaryOut(BaseModel):
    symbol: str
    timeframe: str = Field(min_length=1)
    limit: int
    return_type: str = Field(pattern="^(log|simple)$")
    risk_free_rate: float
    downside_target: float
    observations: int
    mean_return: float | None
    volatility: float | None
    downside_volatility: float | None
    sharpe_ratio: float | None
    sortino_ratio: float | None
    max_drawdown: float | None
