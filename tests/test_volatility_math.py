from datetime import UTC, datetime

from app.domain.analytics.volatility import rolling_std


def test_rolling_std_window_2() -> None:
    values = [
        (datetime(2024, 1, 1, 0, 0, tzinfo=UTC), 0.0),
        (datetime(2024, 1, 1, 1, 0, tzinfo=UTC), 1.0),
        (datetime(2024, 1, 1, 2, 0, tzinfo=UTC), 1.0),
    ]
    out = rolling_std(values=values, window=2)
    assert len(out) == 2
    assert out[0].value >= 0.0
