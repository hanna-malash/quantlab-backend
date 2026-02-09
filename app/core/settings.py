import os
from pathlib import Path


def get_normalized_data_dir() -> Path:
    value = os.getenv("NORMALIZED_DATA_DIR", "data/normalized")
    return Path(value)
