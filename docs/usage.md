# Usage Guide

This guide details how to use the Agentic RAG codebase analyzer, from first setup to advanced conversational and code analysis workflows.

---

## Quick Start

1. **Configure your environment**
    - Copy `config.yaml.example` to `config.yaml`.
    - Fill out all fields, using real credentials, URLs, and deployment names for your database, Ollama embedding service, and Azure OpenAI.

2. **Install dependencies**

    ```sh
    uv pip install .
    ```

3. **Initialize your database**
    - Run the migration script to initialize all required tables, extensions, and indexes for vector search.

    ```sh
    python scripts/migrate_db.py
    ```

    - For minimal setup without indexes/extensions:

    ```sh
    python scripts/init_db.py
    ```

4. **Start the Agentic FastAPI server**

    ```sh
    uvicorn agentic.main:app --reload
    ```

5. **(Optional) Run with Docker**

    ```sh
    docker build -t agentic .
    docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml agentic
    ```

---

## Chatting with the RAG Agent

### Start a New Chat Session

To ask a question or seek code suggestions, POST to the `/chat` endpoint:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "What does the get_ollama_embedding function do?"}'
```

- You may omit the `session_id` in your first request; it will be generated for you in the response.

### Continuing a Session

To keep context, supply the returned `session_id` from the previous response:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "your-session-uuid", "message": "Can you suggest improvements now?"}'
```

---

## Example Conversation

**User:**  
> What does the `get_ollama_embedding` function do?

**Agentic Response:**  
```json
{
  "session_id": "1e0bd9f7-...",
  "reply": "The `get_ollama_embedding` function sends a POST request to the configured Ollama API to obtain a text embedding using the specified model. It returns a vector suitable for semantic search.",
  "history": [
    {
      "role": "user",
      "content": "What does the get_ollama_embedding function do?"
    },
    {
      "role": "assistant",
      "content": "The get_ollama_embedding function sends..."
    }
  ]
}
```

---

## Performing Database Ingestion

Agentic is designed to work with code chunks stored in a Postgres database table (`code_chunks`). To ingest a repo:

- Use `agentic/ingest.py`:  
  This script provides `get_code_chunks(repo_path)` which breaks up Python files into manageable chunks.  
  To use this in practice, create a script or function that:
  1. Calls `get_code_chunks` on your repo.
  2. For each chunk, computes its embedding with your embedder (`get_ollama_embedding` in `agentic/embeddings/ollama.py`).
  3. Inserts `(file_path, chunk, embedding)` tuples into the `code_chunks` table.

**Note:** You may need to write a simple ingestion pipeline script using these functions, as an example is not provided above.

---

## Automated Repo Ingestion

To index a new codebase, run:

```sh
python scripts/ingest_codebase.py /path/to/your/repo
```

This will chunk all Python files, generate embeddings, and insert them into your code chunk database table.

---

## Agentic Management CLI

All admin features are available via `scripts/manage.py`:

- **Ingest a repository**
  ```sh
  python scripts/manage.py ingest /path/to/repo
  ```

- **Clear all Redis chat sessions**
  ```sh
  python scripts/manage.py clear-sessions
  ```

- **Run a test RAG query**
  ```sh
  python scripts/manage.py test-query "What does get_ollama_embedding do?"
  ```

- **Re-index all code chunks (recreate the code_chunks table and embeddings)**
  ```sh
  python scripts/manage.py reindex
  ```

- **Show code chunk statistics**
  ```sh
  python scripts/manage.py stats
  ```

- **Backup with chunk statistics**
  ```sh
  python scripts/manage.py backup-with-stats my_backup_with_stats.json
  ```

This will include total chunk count, average chunk length, and a count of chunks per file in the exported JSON's `summary` section.

You can see all commands and help text with:

```sh
python scripts/manage.py --help
```

---


### Backup and Restore

- **Backup all chunks to a JSON file:**
    ```sh
    python scripts/manage.py backup my_backup.json
    ```

- **Restore chunks from a backup:**
    ```sh
    python scripts/manage.py restore my_backup.json
    ```
    *Note: The restore command will clear all existing code_chunks before restoring from the given backup.*

### Chunk Preview

- **Preview the first 5 code chunks:**
    ```sh
    python scripts/manage.py preview --n 5
    ```
    *Shows file paths and start of chunk text for your inspection.*

### Real Time Log Monitoring

- **Tail logs live (default: agentic.log):**
    ```sh
    python scripts/manage.py tail-log
    # or to tail a specific log file:
    python scripts/manage.py tail-log --logfile path/to/your.log
    ```

    *For this to work, enable file logging in `agentic/logging.py` by uncommenting the log-to-file line.*

---


## Advanced Usage

### Switching Embedding Models

To use a different embedding model (e.g., OpenAI, Azure), update the relevant fields in `config.yaml`, such as `ollama_model` and make sure the `embedding_dim` matches the output dimension of the model.

### Vector Search

Agentic retrieves the most relevant code chunks using a vector similarity search in Postgres (using the `embedding <-> $1` operator).

---

## Troubleshooting

- **App fails at startup**
    - Check logs for missing or invalid `config.yaml` entries. All required fields are listed in `config.yaml.example`.

- **Database or embedding errors**
    - Ensure your database connection string and embedding API URLs are reachable. 
    - Double-check that the embedding dimension in `config.yaml` matches your model and the table.

- **API returns error**
    - Ensure your data is formatted as JSON and all required fields are present.
    - See detailed logs or the response's `error` field for specifics.

- **Pre-commit checks fail**
    - Run `pre-commit run --all-files` locally and review errors before committing.

---

## FAQ

**How do I reset or clear old chat sessions?**  
Use your Redis instance's CLI or a client to delete session keys.

**Where can I see request/response logs?**  
Logs are output to stderr by default. For file logging, see `agentic/logging.py`.

**Can I use this with non-Python code?**  
Chunking in `agentic/ingest.py` currently looks for `.py` files. You can adapt `chunk_code` or add handlers for other languages.

---

## See Also

- [API Reference](api.md)
- [Installation Guide](installation.md)
- [Example Configuration](../config.yaml.example)
- [Test Examples](../tests/test_main.py)