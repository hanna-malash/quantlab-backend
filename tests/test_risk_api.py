import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_risk_summary_endpoint_returns_metrics(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    (normalized_dir / "SPY_1d.csv").write_text(
        "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
        "SPY,2024-01-01T00:00:00+00:00,100,100,100,100,0,stooq,1d\n"
        "SPY,2024-01-02T00:00:00+00:00,110,110,110,110,0,stooq,1d\n"
        "SPY,2024-01-03T00:00:00+00:00,105,105,105,105,0,stooq,1d\n"
        "SPY,2024-01-04T00:00:00+00:00,115,115,115,115,0,stooq,1d\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get("/api/v1/assets/SPY/risk-summary?timeframe=1d&type=log&limit=365")
    assert resp.status_code == 200

    data = resp.json()
    assert data["symbol"] == "SPY"
    assert data["timeframe"] == "1d"
    assert data["return_type"] == "log"
    assert data["observations"] == 3
    assert data["mean_return"] is not None
    assert data["volatility"] is not None
    assert data["downside_volatility"] is not None
    assert data["sharpe_ratio"] is not None
    assert data["sortino_ratio"] is not None
    assert data["max_drawdown"] <= 0.0


def test_risk_summary_endpoint_returns_404_for_missing_data(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get("/api/v1/assets/NOPE/risk-summary?timeframe=1d&type=log&limit=365")
    assert resp.status_code == 404
