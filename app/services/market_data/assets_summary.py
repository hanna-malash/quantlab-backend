from dataclasses import dataclass
from datetime import datetime

from app.core.settings import get_normalized_data_dir
from app.domain.analytics.drawdown import drawdown_series
from app.domain.analytics.returns import log_returns
from app.domain.analytics.volatility import rolling_std
from app.services.market_data.assets_inventory import build_assets_inventory
from app.services.market_data.reader import NormalizedCsvReader

SUMMARY_WINDOW = 30


@dataclass(frozen=True)
class AssetSummary:
    symbol: str
    name: str
    asset_class: str
    currency: str
    available_timeframes: list[str]
    summary_timeframe: str
    summary_window: int
    last_timestamp_utc: datetime | None
    last_close: float | None
    return_30: float | None
    volatility_30: float | None
    max_drawdown: float | None


def _pick_summary_timeframe(timeframes: list[str]) -> str:
    if "1d" in timeframes:
        return "1d"
    if "1h" in timeframes:
        return "1h"
    return timeframes[0]


def _compute_return_30(close_points: list[tuple[datetime, float]]) -> float | None:
    if len(close_points) <= SUMMARY_WINDOW:
        return None

    base_close = close_points[-(SUMMARY_WINDOW + 1)][1]
    last_close = close_points[-1][1]
    if base_close == 0:
        return None
    return (last_close / base_close) - 1.0


def _compute_volatility_30(close_points: list[tuple[datetime, float]]) -> float | None:
    returns_points = log_returns(close_points)
    values = [(r.timestamp_utc, r.value) for r in returns_points]
    volatility_points = rolling_std(values=values, window=SUMMARY_WINDOW)
    if not volatility_points:
        return None
    return volatility_points[-1].value


def _compute_max_drawdown(close_points: list[tuple[datetime, float]]) -> float | None:
    dd_points = drawdown_series(close_points)
    if not dd_points:
        return None
    return min(point.value for point in dd_points)


def build_assets_overview() -> list[AssetSummary]:
    assets = build_assets_inventory()
    reader = NormalizedCsvReader(normalized_dir=get_normalized_data_dir())

    summaries: list[AssetSummary] = []
    for asset in assets:
        timeframes = list(asset["timeframes"])
        if not timeframes:
            continue

        summary_timeframe = _pick_summary_timeframe(timeframes)
        points = reader.read_close_series(
            symbol=str(asset["symbol"]),
            timeframe=summary_timeframe,
            limit=5000,
        )
        close_points = [(p.timestamp_utc, p.close) for p in points]

        last_timestamp_utc = points[-1].timestamp_utc if points else None
        last_close = points[-1].close if points else None

        summaries.append(
            AssetSummary(
                symbol=str(asset["symbol"]),
                name=str(asset["name"]),
                asset_class=str(asset["asset_class"]),
                currency=str(asset["currency"]),
                available_timeframes=timeframes,
                summary_timeframe=summary_timeframe,
                summary_window=SUMMARY_WINDOW,
                last_timestamp_utc=last_timestamp_utc,
                last_close=last_close,
                return_30=_compute_return_30(close_points),
                volatility_30=_compute_volatility_30(close_points),
                max_drawdown=_compute_max_drawdown(close_points),
            )
        )

    return summaries
