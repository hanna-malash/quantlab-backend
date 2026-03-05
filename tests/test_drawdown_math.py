from datetime import UTC, datetime

from app.domain.analytics.drawdown import drawdown_series


def test_drawdown_series() -> None:
    points = [
        (datetime(2024, 1, 1, tzinfo=UTC), 100.0),
        (datetime(2024, 1, 2, tzinfo=UTC), 120.0),
        (datetime(2024, 1, 3, tzinfo=UTC), 90.0),
    ]

    dd = drawdown_series(points)

    assert len(dd) == 3
    assert dd[0].value == 0.0
    assert dd[1].value == 0.0
    assert abs(dd[2].value - (-0.25)) < 1e-12
