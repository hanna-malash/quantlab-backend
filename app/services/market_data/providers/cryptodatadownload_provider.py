import csv
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

from app.schemas.market_data import OhlcvBar


@dataclass
class CryptoDataDownloadSource:
    exchange: str
    symbol: str
    timeframe: str


class CryptoDataDownloadProvider:
    SOURCE_NAME = "cryptodatadownload"

    def load_raw_csv_from_file(self, path: Path) -> list[dict]:
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def load_raw_csv_from_url(self, url: str) -> list[dict]:
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
    ) -> list[OhlcvBar]:
        bars: list[OhlcvBar] = []
        for row in raw_rows:
            date_str = (row.get("date") or row.get("Date") or "").strip()
            if date_str == "":
                continue

            ts = self._parse_datetime_utc(date_str)
            open_v = self._parse_float(row, ["open", "Open"])
            high_v = self._parse_float(row, ["high", "High"])
            low_v = self._parse_float(row, ["low", "Low"])
            close_v = self._parse_float(row, ["close", "Close"])

            # Prefer quote volume if present, otherwise base volume.
            volume_v = self._parse_float_optional(
                row, ["Volume USDT", "Volume USD", "volume", "Volume"]
            )
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
        value = value.strip()
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.replace(tzinfo=UTC)
            except ValueError:
                continue
        raise ValueError(f"Unsupported datetime format: {value}")

    def _parse_float(self, row: dict, keys: list[str]) -> float:
        v = self._parse_float_optional(row, keys)
        if v is None:
            raise ValueError(f"Missing numeric value for keys: {keys}")
        return v

    def _parse_float_optional(self, row: dict, keys: list[str]) -> float | None:
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
