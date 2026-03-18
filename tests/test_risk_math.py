from app.domain.analytics.risk import (
    downside_deviation,
    mean,
    sharpe_ratio,
    sortino_ratio,
    stddev,
)


def test_mean_and_stddev() -> None:
    values = [0.01, 0.02, -0.01]
    assert mean(values) is not None
    assert stddev(values) is not None
    assert mean(values) > 0.0
    assert stddev(values) > 0.0


def test_downside_deviation_uses_only_downside_component() -> None:
    values = [0.03, -0.02, 0.01]
    result = downside_deviation(values)
    assert result is not None
    assert result > 0.0


def test_sharpe_and_sortino() -> None:
    values = [0.02, 0.01, -0.01, 0.03]
    assert sharpe_ratio(values) is not None
    assert sortino_ratio(values) is not None
