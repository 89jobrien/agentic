# Installation & Usage

## 1. Local Development

1. Install dependencies:

    ```sh
    uv pip install .
    ```

2. Start the FastAPI server:

    ```sh
    uvicorn agentic.main:app --reload
    ```

    By default, the API will be available at [http://localhost:8000](http://localhost:8000).

---

## 2. Running with Docker

1. **Build the Docker image:**
    ```sh
    docker build -t agentic .
    ```

2. **Run the container, mounting your config:**
    ```sh
    docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml agentic
    ```

---

## 3. Configuration

1. **Create your configuration:**
    - Copy `config.yaml.example` to `config.yaml`.
    - Fill in all required values (database, embedding model, API keys, etc).
    - For embeddings with `nomic-embed-text`, use `embedding_dim: 768`.

2. **Sample config keys required** (see also `config.yaml.example`):

    ```yaml
    database_url: ...
    ollama_url: ...
    ollama_model: ...
    azure_openai_endpoint: ...
    azure_openai_api_key: ...
    azure_openai_embedding_deployment: ...
    azure_openai_chat_deployment: ...
    azure_openai_api_version: ...
    redis_url: ...
    embedding_dim: ...
    ```

    The system validates your configuration at startup. If any required config is missing or invalid, the startup will fail with a descriptive error message.

---

## 4. Database Setup & Migration

- **Full migration script:**
    ```sh
    python scripts/migrate_db.py
    ```

- **Basic initialization:**
    ```sh
    python scripts/init_db.py
    ```

This will create the `code_chunks` table with the correct embedding vector dimension and index for vector search.

---

## 5. Code Formatting, Typing, and Linting

This project uses:

- **Black** for auto-formatting,
- **Mypy** for static typing,
- **Ruff** for linting.

You can enable pre-commit hooks (recommended):

```sh
pre-commit install
```

Or to check manually before commit:

```sh
pre-commit run --all-files
```

Configuration for these tools is found in `.pre-commit-config.yaml` and `pyproject.toml`.

---

## 6. API Endpoints

### Root

- `GET /`  
  Returns a welcome message.

### Chat

- `POST /chat`  
  Request:
  ```json
  {
    "session_id": "optional-session-id",
    "message": "Ask a question about the codebase"
  }
  ```
  Response:
  ```json
  {
    "session_id": "persisted-or-generated-id",
    "reply": "Model's response",
    "history": [...]
  }
  ```

---

## 7. Logging

- Logging is handled by [Loguru](https://github.com/Delgan/loguru), with setup in `agentic/logging.py`.
- Logs output to stderr by default; you can enable rotating file logging in `agentic/logging.py`.

---

## 8. Troubleshooting

- **App doesn’t start?**  
  Check error output for config validation issues. Verify all required keys are in `config.yaml`.
- **Cannot connect to database?**  
  Ensure the `database_url` is correct and the database is reachable.
- **Embedding errors?**  
  Make sure `ollama_url`/`ollama_model` and the model's dimension (e.g., 768) are correct across config and database.
- **API returns errors?**  
  Check logs for stack traces and diagnostic info.

---

## 9. Additional Info

- To update dependencies, modify `pyproject.toml` and re-run `uv pip install .`
- All code is formatted with Black, which is enforced by pre-commit hooks.
- Test coverage is provided in `tests/`.

---

## 10. Support

If issues persist, review:

- `README.md`
- `config.yaml.example`
- Log outputs (stderr or configured log file)

Or inspect the relevant file in the `agentic/` or `scripts/` directory as indicated by the error message.

---