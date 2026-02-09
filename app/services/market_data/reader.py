import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class PricePoint:
    timestamp_utc: datetime
    close: float


class NormalizedCsvReader:
    def __init__(self, normalized_dir: Path) -> None:
        self._dir = normalized_dir

    def read_close_series(self, symbol: str, timeframe: str, limit: int) -> list[PricePoint]:
        if limit <= 0:
            return []

        path = self._dir / f"{symbol}_{timeframe}.csv"
        if not path.exists():
            raise FileNotFoundError(str(path))

        points: list[PricePoint] = []
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts_str = (row.get("timestamp_utc") or "").strip()
                close_str = (row.get("close") or "").strip()
                if ts_str == "" or close_str == "":
                    continue
                ts = datetime.fromisoformat(ts_str)
                points.append(PricePoint(timestamp_utc=ts, close=float(close_str)))

        points.sort(key=lambda p: p.timestamp_utc)
        if len(points) > limit:
            points = points[-limit:]
        return points
