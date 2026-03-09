import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_drawdown_endpoint_reads_normalized_csv(tmp_path: Path) -> None:
    normalized_dir = tmp_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    (normalized_dir / "SPY_1d.csv").write_text(
        "symbol,timestamp_utc,open,high,low,close,volume,source,timeframe\n"
        "SPY,2024-01-01T00:00:00+00:00,100,100,100,100,0,stooq,1d\n"
        "SPY,2024-01-02T00:00:00+00:00,120,120,120,120,0,stooq,1d\n"
        "SPY,2024-01-03T00:00:00+00:00,90,90,90,90,0,stooq,1d\n",
        encoding="utf-8",
    )

    os.environ["NORMALIZED_DATA_DIR"] = str(normalized_dir)

    client = TestClient(app)
    resp = client.get("/api/v1/assets/SPY/drawdown?timeframe=1d&limit=500")
    assert resp.status_code == 200

    data = resp.json()
    assert data["symbol"] == "SPY"
    assert len(data["points"]) == 3
    assert data["points"][0]["value"] == 0.0
    assert data["points"][1]["value"] == 0.0
    assert abs(data["points"][2]["value"] - (-0.25)) < 1e-12
