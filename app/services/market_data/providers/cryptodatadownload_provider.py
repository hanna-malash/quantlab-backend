import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.request import urlopen

from app.schemas.market_data import OhlcvBar


@dataclass
class CryptoDataDownloadSource:
    exchange: str
    symbol: str
    timeframe: str


class CryptoDataDownloadProvider:
    SOURCE_NAME = "cryptodatadownload"

    def load_raw_csv_from_file(self, path: Path) -> List[dict]:
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def load_raw_csv_from_url(self, url: str) -> List[dict]:
        with urlopen(url) as resp:
            content_bytes = resp.read()
        text = content_bytes.decode("utf-8", errors="replace")
        lines = text.splitlines()
        reader = csv.DictReader(lines)
        return list(reader)

    def normalize(
        self,
        raw_rows: Iterable[dict],
        src: CryptoDataDownloadSource,
    ) -> List[OhlcvBar]:
        bars: List[OhlcvBar] = []
        for row in raw_rows:
            # CryptoDataDownload CSV usually has columns like:
            # date, open, high, low, close, Volume BTC, Volume USDT, tradecount
            # Date can be "2024-01-01 00:00:00" or similar. We'll treat it as UTC.
            date_str = (row.get("date") or row.get("Date") or "").strip()
            if date_str == "":
                continue

            ts = self._parse_datetime_utc(date_str)
            open_v = self._parse_float(row, ["open", "Open"])
            high_v = self._parse_float(row, ["high", "High"])
            low_v = self._parse_float(row, ["low", "Low"])
            close_v = self._parse_float(row, ["close", "Close"])

            # Choose a volume column that exists, prefer quote volume if present, otherwise base volume.
            volume_v = self._parse_float_optional(row, ["Volume USDT", "Volume USD", "volume", "Volume"])
            if volume_v is None:
                volume_v = self._parse_float_optional(row, ["Volume BTC", "Volume ETH"])
            if volume_v is None:
                volume_v = 0.0

            bars.append(
                OhlcvBar(
                    symbol=src.symbol,
                    timestamp_utc=ts,
                    open=open_v,
                    high=high_v,
                    low=low_v,
                    close=close_v,
                    volume=volume_v,
                    source=self.SOURCE_NAME,
                    timeframe=src.timeframe,
                )
            )
        return bars

    def _parse_datetime_utc(self, value: str) -> datetime:
        # Support: "YYYY-MM-DD HH:MM:SS" and "YYYY-MM-DD"
        value = value.strip()
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        # If parsing fails, raise to catch bad inputs early.
        raise ValueError(f"Unsupported datetime format: {value}")

    def _parse_float(self, row: dict, keys: List[str]) -> float:
        v = self._parse_float_optional(row, keys)
        if v is None:
            raise ValueError(f"Missing numeric value for keys: {keys}")
        return v

    def _parse_float_optional(self, row: dict, keys: List[str]) -> Optional[float]:
        for k in keys:
            raw = row.get(k)
            if raw is None:
                continue
            s = str(raw).strip()
            if s == "":
                continue
            try:
                return float(s)
            except ValueError:
                return None
        return None
