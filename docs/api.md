# API Reference

Official documentation for all main Agentic API endpoints.
---

## Root Endpoint
### `GET /`

Returns a welcome message confirming the API is live.

**Response**

```json
{
  "message": "Welcome to Agentic - RAG codebase analyzer."
}
```

---

## Chat Endpoint
### `POST /chat`

Submit user input as a chat turn. Maintains conversational context if `session_id` is provided.
**Request Body**

| Field       | Type   | Required | Description                                       |
|-------------|--------|----------|---------------------------------------------------|
| session_id  | string | no       | Conversation/session identifier                   |
| message     | string | yes      | The user’s question or codebase prompt            |

**Example Request**

```json
{
  "session_id": "a84c7...",
  "message": "How do I connect to the database?"
}
```

**Example Response**
```json
{
  "session_id": "a84c7...",
  "reply": "The database connection is handled using asyncpg in database.py.",
  "history": [
    {"role": "user", "content": "How do I connect to the database?"},
    {"role": "assistant", "content": "The database connection is handled..."}
  ]
}
```

**Behavior**
- If `session_id` is omitted, a new session is started.
- To keep context, pass back the latest `session_id` returned by the server.

---

## Health Check Endpoint
### `GET /health`

Returns API/server status. Useful for deployment orchestration, monitoring, and uptime checks.
**Response**

```json
{
  "status": "ok"
}
```

---

## Analyze Endpoint

### `POST /analyze`

Submit a codebase-related question to receive an answer with supporting context.

**Request Body**  
```json
{
  "question": "How is authentication implemented in this repo?"
}
```

**Response**  
```json
{
  "result": "Summary or snippets with authentication details..."
}
```

**Errors**

- `{"error": "Missing 'question' in request body."}` — If the `question` field is not provided.

---

## Error Handling

All endpoints return error responses as:
```json
{"error": "Description of the error message"}
```
- HTTP 400: User/client errors (e.g., missing fields)
- HTTP 500: Internal server errors

---

## Model Schemas

### Message

```json
{
  "role": "user",
  "content": "string"
}
```

### ChatSession

    ```json
{
  "session_id": "string",
  "messages": [
    {
      "role": "user",
      "content": "string"
    },
    {
      "role": "assistant",
      "content": "string"
    }
  ]
}
```

### CodeChunk

```json
{
  "file_path": "string",
  "chunk": "string"
}
```

---

## Database Table: code_chunks

- Created by `scripts/migrate_db.py` or `scripts/init_db.py`.
- Columns: `id`, `file_path`, `chunk`, `embedding`.
- `embedding` is a `vector(768)` for `nomic-embed-text`.

---

## Example Workflow

1. Ingest code using a script or pipeline calling `get_code_chunks` and `get_ollama_embedding`.
2. Chunks and embeddings are inserted into the database.
3. User queries `/chat`. The backend:
    - Generates a query embedding,
    - Retrieves similar code chunks using Postgres vector search,
    - Constructs a reply with context.

---

## FAQ

- **Can I use this API for multi-turn conversations?**
  Yes. Always provide the `session_id` to maintain context.
- **How do I customize the chunking strategy?**
  Modify or extend `agentic/ingest.py` and `agentic/utils.py`.
- **How do I see all query history?**
  Refer to the `history` field in each `/chat` response.

---

## See Also

- [Usage Guide](usage.md)
- [Installation Guide](installation.md)
- [Configuration Example](../config.yaml.example)
- [Test Coverage](../tests/)
