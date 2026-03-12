import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_assets_overview_endpoint_returns_summary_metrics(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    rows = [
        "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n",
    ]
    close = 100.0
    start = datetime(2024, 1, 1, tzinfo=UTC)
    for day in range(35):
        if day == 20:
            close = 80.0
        else:
            close += 1.0
        ts = start + timedelta(days=day)
        rows.append(f"SPY,{ts.isoformat()},{close},{close},{close},{close},0,stooq,1d\n")

    (normalized_dir / "SPY_1d.csv").write_text("".join(rows), encoding="utf-8")
    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get("/api/v1/assets/overview")
    assert resp.status_code == 200

    data = resp.json()
    assert len(data["assets"]) == 1

    asset = data["assets"][0]
    assert asset["symbol"] == "SPY"
    assert asset["summary_timeframe"] == "1d"
    assert asset["summary_window"] == 30
    assert asset["last_close"] is not None
    assert asset["return_30"] is not None
    assert asset["volatility_30"] is not None
    assert asset["max_drawdown"] < 0.0


def test_assets_overview_uses_intraday_fallback_when_daily_is_missing(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    rows = [
        "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n",
    ]
    close = 40000.0
    start = datetime(2024, 1, 1, tzinfo=UTC)
    for hour in range(40):
        close += 100.0
        ts = start + timedelta(hours=hour)
        rows.append(
            f"BTCUSDT,{ts.isoformat()},{close},{close},{close},{close},0,cryptodatadownload,1h\n"
        )

    (normalized_dir / "BTCUSDT_1h.csv").write_text("".join(rows), encoding="utf-8")
    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get("/api/v1/assets/overview")
    assert resp.status_code == 200

    data = resp.json()
    assert len(data["assets"]) == 1

    asset = data["assets"][0]
    assert asset["symbol"] == "BTCUSDT"
    assert asset["summary_timeframe"] == "1h"
    assert asset["return_30"] is not None
    assert asset["last_close"] is not None
