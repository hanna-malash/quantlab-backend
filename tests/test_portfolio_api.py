import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_portfolio_analytics_endpoint_returns_series_and_summary(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    header = "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
    (normalized_dir / "SPY_1d.csv").write_text(
        header
        + "SPY,2024-01-01T00:00:00+00:00,100,100,100,100,0,stooq,1d\n"
        + "SPY,2024-01-02T00:00:00+00:00,110,110,110,110,0,stooq,1d\n"
        + "SPY,2024-01-03T00:00:00+00:00,105,105,105,105,0,stooq,1d\n",
        encoding="utf-8",
    )
    (normalized_dir / "QQQ_1d.csv").write_text(
        header
        + "QQQ,2024-01-01T00:00:00+00:00,200,200,200,200,0,stooq,1d\n"
        + "QQQ,2024-01-02T00:00:00+00:00,220,220,220,220,0,stooq,1d\n"
        + "QQQ,2024-01-03T00:00:00+00:00,240,240,240,240,0,stooq,1d\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.post(
        "/api/v1/portfolio/analytics",
        json={
            "allocations": [
                {"symbol": "SPY", "weight": 60},
                {"symbol": "QQQ", "weight": 40},
            ],
            "timeframe": "1d",
            "limit": 365,
            "base_value": 100,
            "return_type": "log",
        },
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["timeframe"] == "1d"
    assert data["observations"] == 3
    assert len(data["allocations"]) == 2
    assert abs(data["allocations"][0]["weight"] - 0.6) < 1e-12
    assert data["series"][0]["value"] == 100.0
    assert abs(data["series"][1]["value"] - 110.0) < 1e-12
    assert abs(data["summary"]["total_return"] - 0.11) < 1e-12
    assert data["summary"]["volatility"] is not None
    assert data["summary"]["max_drawdown"] is not None


def test_portfolio_analytics_endpoint_requires_overlapping_points(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    header = "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
    (normalized_dir / "SPY_1d.csv").write_text(
        header + "SPY,2024-01-01T00:00:00+00:00,100,100,100,100,0,stooq,1d\n",
        encoding="utf-8",
    )
    (normalized_dir / "QQQ_1d.csv").write_text(
        header + "QQQ,2024-02-01T00:00:00+00:00,200,200,200,200,0,stooq,1d\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.post(
        "/api/v1/portfolio/analytics",
        json={
            "allocations": [
                {"symbol": "SPY", "weight": 0.5},
                {"symbol": "QQQ", "weight": 0.5},
            ],
            "timeframe": "1d",
        },
    )
    assert resp.status_code == 422
    assert "overlapping observations" in resp.json()["detail"]
