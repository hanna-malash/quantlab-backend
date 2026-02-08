import argparse
from pathlib import Path

from app.services.market_data.providers.cryptodatadownload_provider import (
    CryptoDataDownloadProvider,
    CryptoDataDownloadSource,
)
from app.services.market_data.repository import MarketDataRepository


def main() -> int:
    parser = argparse.ArgumentParser(
        description="QuantLab data ingestion (raw CSV -> normalized CSV)."
    )
    parser.add_argument("--source", choices=["cryptodatadownload"], required=True)

    parser.add_argument("--exchange", required=True, help="Example: binance")
    parser.add_argument("--symbol", required=True, help="Example: BTCUSDT")
    parser.add_argument("--timeframe", required=True, help="Example: 1h or 1d")

    parser.add_argument(
        "--raw-file",
        default="",
        help="Path to raw CSV file (preferred for reproducibility).",
    )
    parser.add_argument("--url", default="", help="Optional URL to download raw CSV.")
    parser.add_argument(
        "--normalized-dir",
        default="data/normalized",
        help="Output directory for normalized CSV.",
    )

    args = parser.parse_args()

    provider = CryptoDataDownloadProvider()
    src = CryptoDataDownloadSource(
        exchange=args.exchange,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )

    raw_file = args.raw_file.strip()
    url = args.url.strip()

    if raw_file == "" and url == "":
        print("Error: provide either --raw-file or --url")
        return 2

    if raw_file != "":
        raw_rows = provider.load_raw_csv_from_file(Path(raw_file))
    else:
        raw_rows = provider.load_raw_csv_from_url(url)

    bars = provider.normalize(raw_rows=raw_rows, src=src)

    repo = MarketDataRepository(normalized_dir=Path(args.normalized_dir))
    output_path = repo.write_bars_csv(
        bars=bars,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )

    print(f"Normalized bars: {len(bars)}")
    print(f"Saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
