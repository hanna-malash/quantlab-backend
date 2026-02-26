import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_prices_endpoint_reads_normalized_csv(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    csv_path = normalized_dir / "BTCUSDT_1h.csv"
    csv_path.write_text(
        "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
        "BTCUSDT,2024-01-01T00:00:00+00:00,42000,42100,41900,42050,420500,cryptodatadownload,1h\n"
        "BTCUSDT,2024-01-01T01:00:00+00:00,42050,42200,42000,42150,505800,cryptodatadownload,1h\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get("/api/v1/assets/BTCUSDT/prices?timeframe=1h&limit=500")
    assert resp.status_code == 200

    data = resp.json()
    assert data["symbol"] == "BTCUSDT"
    assert len(data["points"]) == 2
    assert data["points"][0]["timestamp_utc"].startswith("2024-01-01T00:00:00")
    assert data["points"][0]["close"] == 42050.0
