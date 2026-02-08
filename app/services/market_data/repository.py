import csv
from collections.abc import Iterable
from pathlib import Path

from app.schemas.market_data import OhlcvBar


class MarketDataRepository:
    def __init__(self, normalized_dir: Path) -> None:
        self._normalized_dir = normalized_dir

    def write_bars_csv(self, bars: Iterable[OhlcvBar], symbol: str, timeframe: str) -> Path:
        self._normalized_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._normalized_dir / f"{symbol}_{timeframe}.csv"
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "symbol",
                    "timestamp_utc",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "source",
                    "timeframe",
                ]
            )
            for bar in bars:
                writer.writerow(
                    [
                        bar.symbol,
                        bar.timestamp_utc.isoformat(),
                        bar.open,
                        bar.high,
                        bar.low,
                        bar.close,
                        bar.volume,
                        bar.source,
                        bar.timeframe,
                    ]
                )
        return output_path
