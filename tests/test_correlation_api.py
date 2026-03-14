import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_correlation_endpoint_returns_matrix_for_aligned_assets(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    header = "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
    (normalized_dir / "SPY_1d.csv").write_text(
        header
        + "SPY,2024-01-01T00:00:00+00:00,100,100,100,100,0,stooq,1d\n"
        + "SPY,2024-01-02T00:00:00+00:00,101,101,101,101,0,stooq,1d\n"
        + "SPY,2024-01-03T00:00:00+00:00,103,103,103,103,0,stooq,1d\n"
        + "SPY,2024-01-04T00:00:00+00:00,106,106,106,106,0,stooq,1d\n",
        encoding="utf-8",
    )
    (normalized_dir / "QQQ_1d.csv").write_text(
        header
        + "QQQ,2024-01-01T00:00:00+00:00,200,200,200,200,0,stooq,1d\n"
        + "QQQ,2024-01-02T00:00:00+00:00,202,202,202,202,0,stooq,1d\n"
        + "QQQ,2024-01-03T00:00:00+00:00,206,206,206,206,0,stooq,1d\n"
        + "QQQ,2024-01-04T00:00:00+00:00,212,212,212,212,0,stooq,1d\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get(
        "/api/v1/analytics/correlation?symbols=SPY&symbols=QQQ&timeframe=1d&limit=365"
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["symbols"] == ["SPY", "QQQ"]
    assert data["timeframe"] == "1d"
    assert data["observations"] == 3
    assert len(data["rows"]) == 2
    assert data["rows"][0]["values"][0] == 1.0
    assert data["rows"][1]["values"][1] == 1.0
    assert abs(data["rows"][0]["values"][1] - 1.0) < 1e-12
    assert abs(data["rows"][1]["values"][0] - 1.0) < 1e-12


def test_correlation_endpoint_requires_overlapping_observations(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    header = "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
    (normalized_dir / "SPY_1d.csv").write_text(
        header
        + "SPY,2024-01-01T00:00:00+00:00,100,100,100,100,0,stooq,1d\n"
        + "SPY,2024-01-02T00:00:00+00:00,101,101,101,101,0,stooq,1d\n",
        encoding="utf-8",
    )
    (normalized_dir / "QQQ_1d.csv").write_text(
        header
        + "QQQ,2024-02-01T00:00:00+00:00,200,200,200,200,0,stooq,1d\n"
        + "QQQ,2024-02-02T00:00:00+00:00,201,201,201,201,0,stooq,1d\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get(
        "/api/v1/analytics/correlation?symbols=SPY&symbols=QQQ&timeframe=1d&limit=365"
    )
    assert resp.status_code == 422
    assert "overlapping observations" in resp.json()["detail"]
