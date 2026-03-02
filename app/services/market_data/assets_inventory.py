import os
from pathlib import Path
from typing import Dict, List


def _get_normalized_data_dir() -> Path:
    env_value = os.environ.get("NORMALIZED_DATA_DIR")
    if env_value:
        return Path(env_value)
    return Path("data") / "normalized"


def build_assets_inventory() -> List[Dict[str, object]]:
    normalized_dir = _get_normalized_data_dir()
    inventory: Dict[str, List[str]] = {}

    if not normalized_dir.exists() or not normalized_dir.is_dir():
        return []

    for file_path in normalized_dir.glob("*.csv"):
        stem = file_path.stem  # e.g. "BTCUSDT_1h"
        if "_" not in stem:
            continue

        # split by last underscore to support symbols that might contain underscores later
        parts = stem.rsplit("_", 1)
        if len(parts) != 2:
            continue

        symbol = parts[0].strip()
        timeframe = parts[1].strip()

        if symbol == "" or timeframe == "":
            continue

        if symbol not in inventory:
            inventory[symbol] = []

        if timeframe not in inventory[symbol]:
            inventory[symbol].append(timeframe)

    # Stable output: sort symbols and timeframes
    assets: List[Dict[str, object]] = []
    for symbol in sorted(inventory.keys()):
        timeframes = sorted(inventory[symbol])
        assets.append(
            {
                "symbol": symbol,
                "name": symbol,
                "asset_class": "unknown",
                "currency": "unknown",
                "timeframes": timeframes,
            }
        )
    return assets