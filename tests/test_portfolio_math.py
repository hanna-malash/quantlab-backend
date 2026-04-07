from datetime import UTC, datetime

from app.domain.analytics.portfolio import (
    PortfolioAllocation,
    build_portfolio_series,
    normalize_allocations,
    portfolio_max_drawdown,
    portfolio_total_return,
    portfolio_volatility,
)


def test_normalize_allocations_scales_weights_to_one() -> None:
    allocations = normalize_allocations(
        [
            PortfolioAllocation(symbol="spy", weight=60),
            PortfolioAllocation(symbol="qqq", weight=40),
        ]
    )

    assert allocations[0].symbol == "SPY"
    assert allocations[1].symbol == "QQQ"
    assert abs(sum(item.weight for item in allocations) - 1.0) < 1e-12
    assert abs(allocations[0].weight - 0.6) < 1e-12


def test_build_portfolio_series_and_summary_metrics() -> None:
    allocations = normalize_allocations(
        [
            PortfolioAllocation(symbol="SPY", weight=0.6),
            PortfolioAllocation(symbol="QQQ", weight=0.4),
        ]
    )

    timestamps = [
        datetime(2024, 1, 1, tzinfo=UTC),
        datetime(2024, 1, 2, tzinfo=UTC),
        datetime(2024, 1, 3, tzinfo=UTC),
    ]
    series = build_portfolio_series(
        allocations=allocations,
        series_by_symbol={
            "SPY": list(zip(timestamps, [100.0, 110.0, 95.0], strict=True)),
            "QQQ": list(zip(timestamps, [200.0, 220.0, 180.0], strict=True)),
        },
        base_value=100.0,
    )

    assert len(series) == 3
    assert abs(series[0].value - 100.0) < 1e-12
    assert abs(series[1].value - 110.0) < 1e-12
    assert abs(series[2].value - 93.0) < 1e-12
    assert abs(portfolio_total_return(series) - (-0.07)) < 1e-12
    assert portfolio_volatility(series, "log") is not None
    assert abs(portfolio_max_drawdown(series) - (-0.15454545454545454)) < 1e-12
