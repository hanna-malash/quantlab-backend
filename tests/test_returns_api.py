import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_returns_endpoint_log(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    csv_path = normalized_dir / "BTCUSDT_1h.csv"
    csv_path.write_text(
        "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
        "BTCUSDT,2024-01-01T00:00:00+00:00,1,1,1,100,1,cryptodatadownload,1h\n"
        "BTCUSDT,2024-01-01T01:00:00+00:00,1,1,1,110,1,cryptodatadownload,1h\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get("/api/v1/assets/BTCUSDT/returns?timeframe=1h&type=log&limit=500")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["value"] > 0.0
