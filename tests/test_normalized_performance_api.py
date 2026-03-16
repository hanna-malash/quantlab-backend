import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_normalized_performance_endpoint_returns_base_100_series(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    header = "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
    (normalized_dir / "SPY_1d.csv").write_text(
        header
        + "SPY,2024-01-01T00:00:00+00:00,100,100,100,100,0,stooq,1d\n"
        + "SPY,2024-01-02T00:00:00+00:00,110,110,110,110,0,stooq,1d\n"
        + "SPY,2024-01-03T00:00:00+00:00,120,120,120,120,0,stooq,1d\n",
        encoding="utf-8",
    )
    (normalized_dir / "QQQ_1d.csv").write_text(
        header
        + "QQQ,2024-01-01T00:00:00+00:00,200,200,200,200,0,stooq,1d\n"
        + "QQQ,2024-01-02T00:00:00+00:00,220,220,220,220,0,stooq,1d\n"
        + "QQQ,2024-01-03T00:00:00+00:00,210,210,210,210,0,stooq,1d\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get(
        "/api/v1/analytics/normalized-performance?symbols=SPY&symbols=QQQ&timeframe=1d&limit=365"
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["symbols"] == ["SPY", "QQQ"]
    assert data["timeframe"] == "1d"
    assert data["observations"] == 3
    assert data["base_value"] == 100.0
    assert len(data["series"]) == 2
    assert data["series"][0]["points"][0]["value"] == 100.0
    assert data["series"][1]["points"][0]["value"] == 100.0
    assert abs(data["series"][0]["points"][1]["value"] - 110.0) < 1e-12
    assert abs(data["series"][1]["points"][2]["value"] - 105.0) < 1e-12


def test_normalized_performance_endpoint_requires_overlapping_points(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    header = "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
    (normalized_dir / "SPY_1d.csv").write_text(
        header
        + "SPY,2024-01-01T00:00:00+00:00,100,100,100,100,0,stooq,1d\n",
        encoding="utf-8",
    )
    (normalized_dir / "QQQ_1d.csv").write_text(
        header
        + "QQQ,2024-02-01T00:00:00+00:00,200,200,200,200,0,stooq,1d\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get(
        "/api/v1/analytics/normalized-performance?symbols=SPY&symbols=QQQ&timeframe=1d&limit=365"
    )
    assert resp.status_code == 422
    assert "overlapping observations" in resp.json()["detail"]
