# QuantLab Backend

![CI](https://github.com/hanna-malash/QuantLab/actions/workflows/ci.yml/badge.svg)

FastAPI backend for market data analytics. The service exposes HTTP endpoints for price series, returns, volatility, drawdown, and asset discovery based on normalized CSV data.

## Stack

- Python 3.13+
- FastAPI
- uv
- ruff
- pytest
- pre-commit

## Project layout

```text
app/
├── api/                    # FastAPI routes and router wiring
├── core/                   # shared settings
├── domain/analytics/       # pure calculation logic
├── schemas/                # response models
├── scripts/                # data normalization / ingestion
└── services/market_data/   # CSV readers, repository, providers

data/
├── raw/                    # source files before normalization
└── normalized/             # API-ready OHLCV files

tests/                      # API and domain tests
```

The separation is intentional:

- `app/domain/analytics` contains math only
- `app/api` stays thin and delegates to services/domain logic
- `app/services/market_data` handles file access and provider-specific normalization

## Setup

Install dependencies from the repository root:

```bash
uv sync
```

If `uv` is not installed yet:

```bash
brew install uv
```

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/api/v1/health`

## API endpoints

Base prefix: `/api/v1`

- `GET /health`
- `GET /assets`
- `GET /assets/{symbol}/prices`
- `GET /assets/{symbol}/returns`
- `GET /assets/{symbol}/volatility`
- `GET /assets/{symbol}/drawdown`

Examples:

```bash
curl "http://127.0.0.1:8000/api/v1/assets"
curl "http://127.0.0.1:8000/api/v1/assets/BTCUSDT/returns?timeframe=1h&type=log&limit=100"
curl "http://127.0.0.1:8000/api/v1/assets/BTCUSDT/volatility?timeframe=1h&window=24&limit=200"
```

## Data

The API reads normalized CSV files from `data/normalized/` by default.

Examples already present in the repository:

- `BTCUSDT_1h.csv`
- `SPY_1d.csv`
- `QQQ_1d.csv`
- `SPX_1d.csv`
- `EURUSD_1d.csv`
- `XAUUSD_1d.csv`

You can override the input directory with:

```bash
export NORMALIZED_DATA_DIR=/path/to/normalized
```

File naming convention:

```text
<SYMBOL>_<TIMEFRAME>.csv
```

## Normalize raw data

To convert a raw CryptoDataDownload CSV into the normalized format:

```bash
uv run python -m app.scripts.ingest \
  --source cryptodatadownload \
  --exchange binance \
  --symbol BTCUSDT \
  --timeframe 1h \
  --raw-file data/raw/BTCUSDT_1h.csv
```

The normalized file will be written to `data/normalized/`.

## Quality checks

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```

To run a specific API test:

```bash
uv run pytest tests/test_returns_api.py
```

## Notes

- `GET /assets` builds its response from the CSV files available in the normalized data directory.
- Analytics endpoints return `404` if the requested `{symbol}_{timeframe}.csv` file does not exist.
- The project currently uses file-based market data, not a database.
