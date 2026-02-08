from pathlib import Path

from app.services.market_data.providers.cryptodatadownload_provider import (
    CryptoDataDownloadProvider,
    CryptoDataDownloadSource,
)
from app.services.market_data.repository import MarketDataRepository


def test_cryptodatadownload_normalize_and_write(tmp_path: Path) -> None:
    provider = CryptoDataDownloadProvider()
    src = CryptoDataDownloadSource(exchange="binance", symbol="BTCUSDT", timeframe="1h")

    fixture_path = Path("tests/fixtures/cryptodd_btcusdt_1h_sample.csv")
    raw_rows = provider.load_raw_csv_from_file(fixture_path)

    bars = provider.normalize(raw_rows=raw_rows, src=src)
    assert len(bars) == 2
    assert bars[0].symbol == "BTCUSDT"
    assert bars[0].timeframe == "1h"
    assert bars[0].open == 42000.0
    assert bars[0].close == 42050.0

    repo = MarketDataRepository(normalized_dir=tmp_path)
    out_path = repo.write_bars_csv(bars=bars, symbol="BTCUSDT", timeframe="1h")

    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe" in content
    assert "BTCUSDT" in content
