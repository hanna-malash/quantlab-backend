# QuantLab Backend

Backend service for **QuantLab** — a finance-focused analytics platform for crypto, stocks and portfolio analytics.

The goal of this backend is to provide:

- a clean FastAPI-based HTTP API
- a well-separated computation core (returns, volatility, VaR/CVaR, portfolio metrics)
- strict engineering discipline (small PRs, tests, formatting, documentation)

This repository is intentionally structured to separate:

- API layer (FastAPI)
- domain logic (pure math / finance)
- integrations (external data sources, DB later)
- tests

Every feature is developed in its own branch and merged via Pull Request.

---

## Tech stack

- Python 3.13
- FastAPI (API layer – coming in next features)
- uv (dependency management + command runner)
- ruff (lint + formatter)
- pytest (tests)
- pre-commit (pre-commit + pre-push hooks)

---

## Repository structure (high level)

```
app/
├── api/              # HTTP routes (FastAPI)
├── core/             # config, shared helpers
├── domain/           # pure finance / math logic (no FastAPI, no DB)
├── services/         # integrations (market data providers, later DB)
├── schemas/          # Pydantic models
└── db/               # database layer (future)
tests/
docs/
```

Key idea:

- `domain/` contains only calculations
- `api/` is just a thin HTTP layer
- `services/` talk to the outside world
- `tests/` verify everything

---

## Requirements

- Python 3.13
- uv

---

## Install uv

### macOS

```bash
brew install uv
uv --version
```

### Windows (inside virtual environment)

If `winget` does not work, install via pip:

```bash
python -m ensurepip --upgrade
python -m pip install -U uv
python -m uv --version
```

## Setup dependencies

From repository root:

```

If you add packages later:

```bash
uv add <package>
uv add --dev <package>
```

## Running the project

FastAPI entrypoint will be added in a separate feature PR.

When available, the API will be started with:

```bash
uv run uvicorn app.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## Code quality

### Ruff – lint

```bash
uv run ruff check .
```

### Ruff – format

```bash
uv run ruff format .
```

## Tests

Run all tests:

```bash
uv run pytest
```

Run a single test file:

```bash
uv run pytest tests/test_returns.py
```

## Git hooks (pre-commit + pre-push)

This repository uses pre-commit with:

- ruff (auto-fix)
- ruff-format

### Install hooks (one-time per machine)

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

### Run hooks manually

```bash
uv run pre-commit run --all-files
```

If hooks do not trigger automatically:

- make sure they are installed
- restart terminal (especially on Windows)
- confirm you are inside this repo

## Development workflow (must follow)

### Update local master

```bash
git checkout master
git pull
```

### Create feature branch

```bash
git checkout -b feature/<short-name>
```

### Implement feature

Rules:

- domain logic → app/domain
- API wiring → app/api
- integrations → app/services
- tests → tests

### Run checks locally

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
uv run pre-commit run --all-files
```

### Commit and push

```bash
git add .
git commit -m "<type>: <message>"
git push -u origin feature/<short-name>
```

### Open Pull Request

Every PR must:

- be small and focused
- include tests (when applicable)
- update README or docs if behavior changes

## Common issues

### uv not found

macOS:

```bash
brew install uv
```

Windows:

```bash
python -m pip install -U uv
python -m uv --version
```

### No module named pip

Your venv is missing pip:

```bash
python -m ensurepip --upgrade
python -m pip --version
```

### Hooks not running

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

Restart terminal afterwards.

## Project philosophy

QuantLab is built as an applied quantitative project:

- correctness over speed
- explicit math over magic ML
- small PRs
- reproducible calculations
- clear separation of concerns

This is a learning + portfolio project with production-style discipline.

## License

TBD