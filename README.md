# Agentic

A Retrieval Augmented Generation (RAG) agent that analyzes code repositories and suggests improvements.

## Configuration

1. Copy `config.yaml.example` to `config.yaml`.
2. Fill in the values for all keys:
   - `database_url`: Your database connection string (e.g., for Postgres).
   - `ollama_url`: Local URL for Ollama embedding API.
   - `ollama_model`: The embedding model to use with Ollama.
   - `azure_openai_*`: Required Azure OpenAI API settings.
   - `redis_url`: URL for your Redis session store (if used).

## Running

### Local

```bash
uv pip install .
uvicorn agentic.main:app --reload
```

### Docker

```bash
docker build -t agentic .
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml agentic
```

## Linting & Code Quality

This project uses [pre-commit](https://pre-commit.com/) with:

- [Black](https://github.com/psf/black) for code formatting
- [Mypy](https://github.com/python/mypy) for static type checking
- [Ruff](https://github.com/astral-sh/ruff) for linting

To enable locally, install pre-commit and register hooks:

```sh
pre-commit install
```

To run checks manually:

```sh
pre-commit run --all-files
```

Configuration for these tools is found in `.pre-commit-config.yaml` and `pyproject.toml`.

## API Endpoints

- `GET /` — Welcome message.
- `POST /chat` — Chat endpoint.
  Request JSON:
  ```json
  {
    "session_id": "optional-session-id",
    "message": "Hello, agent!"
  }

## Additional Documentation

- [Installation & Usage Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [API Reference](docs/api.md)
- Example configuration: `config.yaml.example`
- Database setup scripts: `scripts/init_db.py`, `scripts/migrate_db.py`
- See also `tests/` for automated test examples

## CLI and Admin Scripts

Most operational features (ingestion, session management, statistics, reindexing, testing) are provided through a unified CLI:

```sh
python scripts/manage.py --help
```
[![pre-commit enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
