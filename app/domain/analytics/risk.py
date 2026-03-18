import math


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def stddev(values: list[float]) -> float | None:
    if len(values) < 2:
        return None

    avg = mean(values)
    if avg is None:
        return None

    variance = sum((value - avg) * (value - avg) for value in values) / len(values)
    return math.sqrt(variance)


def downside_deviation(values: list[float], target: float = 0.0) -> float | None:
    if not values:
        return None

    downside = [min(0.0, value - target) for value in values]
    variance = sum(value * value for value in downside) / len(downside)
    return math.sqrt(variance)


def sharpe_ratio(values: list[float], risk_free_rate: float = 0.0) -> float | None:
    if len(values) < 2:
        return None

    excess_returns = [value - risk_free_rate for value in values]
    avg_excess = mean(excess_returns)
    volatility = stddev(values)

    if avg_excess is None or volatility in (None, 0.0):
        return None

    return avg_excess / volatility


def sortino_ratio(
    values: list[float],
    risk_free_rate: float = 0.0,
    target: float = 0.0,
) -> float | None:
    if len(values) < 2:
        return None

    excess_returns = [value - risk_free_rate for value in values]
    avg_excess = mean(excess_returns)
    downside_volatility = downside_deviation(values, target=target)

    if avg_excess is None or downside_volatility in (None, 0.0):
        return None

    return avg_excess / downside_volatility
