import csv
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class PricePoint:
    timestamp_utc: datetime
    close: float


class NormalizedCsvReader:
    def __init__(self, normalized_dir: Path) -> None:
        self._dir = normalized_dir

    def _parse_timestamp(self, raw: str) -> datetime:
        value = raw.strip()
        if value == "":
            raise ValueError("empty timestamp")

        # If format is "YYYY-MM-DD HH:MM:SS" (CryptoDataDownload), treat as UTC.
        if "T" not in value and " " in value:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return dt.replace(tzinfo=UTC)

        # Otherwise try ISO 8601 (with or without timezone).
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt

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
                ts_str = (row.get("timestamp_utc") or row.get("date") or "").strip()
                close_str = (row.get("close") or "").strip()
                if ts_str == "" or close_str == "":
                    continue

                try:
                    ts = self._parse_timestamp(ts_str)
                    close = float(close_str)
                except ValueError:
                    continue

                points.append(PricePoint(timestamp_utc=ts, close=close))

        points.sort(key=lambda p: p.timestamp_utc)
        if len(points) > limit:
            points = points[-limit:]
        return points
