import csv
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class StooqRow:
    date: str
    open: str
    high: str
    low: str
    close: str
    volume: str


def _to_float(value: str) -> float:
    v = value.strip()
    if v == "":
        return 0.0
    return float(v)


def _to_int(value: str) -> int:
    v = value.strip()
    if v == "":
        return 0
    return int(float(v))


def _date_to_timestamp_utc(date_str: str) -> str:
    dt = datetime.strptime(date_str.strip(), "%Y-%m-%d").replace(tzinfo=UTC)
    return dt.isoformat()


def _pick(r: dict, keys: list[str]) -> str:
    for k in keys:
        if k in r and r[k] is not None:
            v = str(r[k]).strip()
            if v != "":
                return v
    return ""


def _read_stooq_csv(path: Path) -> list[StooqRow]:
    rows: list[StooqRow] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r is None:
                continue

            date = _pick(r, ["Date", "Data"])
            if date == "":
                continue

            open_v = _pick(r, ["Open", "Otwarcie"])
            high_v = _pick(r, ["High", "Najwyzszy"])
            low_v = _pick(r, ["Low", "Najnizszy"])
            close_v = _pick(r, ["Close", "Zamkniecie"])

            # Some Stooq exports may omit Volume (e.g. XAUUSD)
            volume_v = _pick(r, ["Volume", "Wolumen"])
            if volume_v == "":
                volume_v = "0"

            rows.append(
                StooqRow(
                    date=date,
                    open=open_v,
                    high=high_v,
                    low=low_v,
                    close=close_v,
                    volume=volume_v,
                )
            )

    rows.sort(key=lambda x: x.date)
    return rows


def _write_normalized_csv(
    out_path: Path, symbol: str, timeframe: str, source: str, rows: list[StooqRow]
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
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
        for r in rows:
            writer.writerow(
                [
                    symbol,
                    _date_to_timestamp_utc(r.date),
                    _to_float(r.open),
                    _to_float(r.high),
                    _to_float(r.low),
                    _to_float(r.close),
                    _to_int(r.volume),
                    source,
                    timeframe,
                ]
            )


def normalize_one_file(raw_path: Path, normalized_dir: Path) -> Path | None:
    name = raw_path.name.lower()

    mapping = {
        "spy_us_d.csv": "SPY",
        "qqq_us_d.csv": "QQQ",
        "eurusd_d.csv": "EURUSD",
        "xauusd_d.csv": "XAUUSD",
        "^spx_d.csv": "SPX",
    }

    symbol = mapping.get(name)
    if symbol is None:
        return None

    timeframe = "1d"
    source = "stooq"

    rows = _read_stooq_csv(raw_path)
    out_path = normalized_dir / f"{symbol}_{timeframe}.csv"
    _write_normalized_csv(out_path, symbol, timeframe, source, rows)
    return out_path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    raw_dir = repo_root / "data" / "raw"
    normalized_dir = repo_root / "data" / "normalized"

    if not raw_dir.exists():
        print(f"Raw dir not found: {raw_dir}")
        return 1

    written: list[Path] = []
    for p in sorted(raw_dir.glob("*.csv")):
        out = normalize_one_file(p, normalized_dir)
        if out is not None:
            written.append(out)

    if not written:
        print("No files normalized.")
        return 1

    for p in written:
        print(f"Normalized: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
