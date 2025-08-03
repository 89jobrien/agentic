# Using the manage tool

## Initialize your database (run this once)
`uv run scripts/manage.py db init`

## Ingest your codebase (replace '.' with the path to your code)
`uv run scripts/manage.py ingest .`

## Ask a question
`uv run scripts/manage.py query "What does the SessionStore class do?"`

## See database statistics
`uv run scripts/manage.py db stats`

## Test your Ollama connection
`uv run scripts/manage.py test-embedding`

## Clear all chat histories from Redis
`uv run scripts/manage.py clear-sessions`