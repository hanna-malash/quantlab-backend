# tests/test_assets_api.py

import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_assets_endpoint_lists_symbols_from_normalized_dir(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    (normalized_dir / "BTCUSDT_1h.csv").write_text("header\n", encoding="utf-8")
    (normalized_dir / "ETHUSDT_1h.csv").write_text("header\n", encoding="utf-8")
    (normalized_dir / "AAPL_1d.csv").write_text("header\n", encoding="utf-8")

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get("/api/v1/assets")
    assert resp.status_code == 200

    data = resp.json()
    assert "assets" in data

    # Convert list to dict for easier asserts
    assets_by_symbol = {}
    for a in data["assets"]:
        assets_by_symbol[a["symbol"]] = a

    assert "BTCUSDT" in assets_by_symbol
    assert "ETHUSDT" in assets_by_symbol
    assert "AAPL" in assets_by_symbol

    assert "1h" in assets_by_symbol["BTCUSDT"]["timeframes"]
    assert "1h" in assets_by_symbol["ETHUSDT"]["timeframes"]
    assert "1d" in assets_by_symbol["AAPL"]["timeframes"]