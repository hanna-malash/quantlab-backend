import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CorrelationRow:
    symbol: str
    values: list[float]


def align_series(
    series_by_symbol: dict[str, list[tuple[datetime, float]]],
) -> dict[str, list[float]]:
    values_by_timestamp: dict[datetime, dict[str, float]] = defaultdict(dict)
    for symbol, points in series_by_symbol.items():
      for timestamp_utc, value in points:
            values_by_timestamp[timestamp_utc][symbol] = value

    aligned_timestamps = sorted(
        timestamp
        for timestamp, values in values_by_timestamp.items()
        if len(values) == len(series_by_symbol)
    )

    aligned: dict[str, list[float]] = {symbol: [] for symbol in series_by_symbol}
    for timestamp in aligned_timestamps:
        row = values_by_timestamp[timestamp]
        for symbol in series_by_symbol:
            aligned[symbol].append(row[symbol])

    return aligned


def pearson_correlation(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("correlation requires at least two aligned values")

    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)

    numerator = 0.0
    left_var = 0.0
    right_var = 0.0
    for left_value, right_value in zip(left, right, strict=True):
        left_delta = left_value - mean_left
        right_delta = right_value - mean_right
        numerator += left_delta * right_delta
        left_var += left_delta * left_delta
        right_var += right_delta * right_delta

    if left_var == 0.0 or right_var == 0.0:
        return 0.0

    return numerator / math.sqrt(left_var * right_var)


def correlation_matrix(
    symbols: list[str],
    aligned_returns: dict[str, list[float]],
) -> list[CorrelationRow]:
    rows: list[CorrelationRow] = []
    for row_symbol in symbols:
        values: list[float] = []
        for col_symbol in symbols:
            if row_symbol == col_symbol:
                values.append(1.0)
                continue

            values.append(
                pearson_correlation(
                    aligned_returns[row_symbol],
                    aligned_returns[col_symbol],
                )
            )
        rows.append(CorrelationRow(symbol=row_symbol, values=values))
    return rows
