import math
from datetime import UTC, datetime

from app.domain.analytics.returns import log_returns, simple_returns


def test_simple_returns_basic() -> None:
    points = [
        (datetime(2024, 1, 1, 0, 0, tzinfo=UTC), 100.0),
        (datetime(2024, 1, 1, 1, 0, tzinfo=UTC), 110.0),
    ]
    out = simple_returns(points)
    assert len(out) == 1
    assert math.isclose(out[0].value, 0.1, rel_tol=1e-12, abs_tol=0.0)


def test_log_returns_basic() -> None:
    points = [
        (datetime(2024, 1, 1, 0, 0, tzinfo=UTC), 100.0),
        (datetime(2024, 1, 1, 1, 0, tzinfo=UTC), 110.0),
    ]
    out = log_returns(points)
    assert len(out) == 1
    assert out[0].value > 0.0
