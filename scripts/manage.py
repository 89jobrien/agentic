import asyncio
import typer
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

from agentic.config import config
from agentic.models import Message
from agentic.database import get_db_pool, close_db_pool
from agentic.rag_agent import RAGAgent
from agentic.utils import get_project_name


# ------------------------------
# --- Setup ---
console = Console()
app = typer.Typer(
    name="agentic",
    help="🤖 [bold]A CLI for managing the Agentic RAG codebase analyzer.[/bold]",
    rich_markup_mode="rich",
    add_completion=False,
)
db_app = typer.Typer(
    help="🗄️ Commands for database management (init, stats, backup, etc.)",
    rich_markup_mode="rich",
)
app.add_typer(db_app)


# ------------------------------
# --- DB Init ---


def _db_init_logic():
    async def run():
        pool = await get_db_pool()
        console.print("Creating 'vector' extension if it doesn't exist...")
        await pool.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        console.print("Creating 'code_chunks' table if it doesn't exist...")
        await pool.execute(f"""
            CREATE TABLE IF NOT EXISTS code_chunks (
                id TEXT PRIMARY KEY,
                repo_name TEXT,
                file_path TEXT,
                chunk TEXT,
                embedding vector({config.llm.embedding_dim})
            );
            """)
        console.print("Creating IVF flat index on embeddings...")
        await pool.execute("""
        CREATE INDEX IF NOT EXISTS code_chunks_embedding_idx
        ON code_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        """)
        await close_db_pool()
        console.print("[bold green]Database initialization complete.[/bold green]")

    asyncio.run(run())


@db_app.command(
    "init",
    short_help="dbi: Initializes the database schema and extensions.",
    help="Creates the [bold]vector[/bold] extension and the [bold]code_chunks[/bold] table with a vector index. This command should be run once before using the application.",
)
def db_init():
    _db_init_logic()


@db_app.command(
    "dbi",
    help="Creates the [bold]vector[/bold] extension and the [bold]code_chunks[/bold] table with a vector index. This command should be run once before using the application.",
    hidden=True,
)
def db_init_alias():
    _db_init_logic()


# ------------------------------
# --- DB Stats ---


def _format_bytes(size: float) -> str:
    """Helper function to format bytes into KB, MB, etc."""
    if size is None:
        return "N/A"
    power = 1024
    n = 0
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power and n < len(power_labels) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"


def _db_stats_logic():
    async def run():
        pool = await get_db_pool()

        # --- Fetch summary statistics in one query for efficiency ---
        summary_query = """
        SELECT
            COUNT(*) AS total_chunks,
            AVG(LENGTH(chunk)) AS avg_chunk_len,
            MIN(LENGTH(chunk)) AS min_chunk_len,
            MAX(LENGTH(chunk)) AS max_chunk_len,
            SUM(LENGTH(chunk)) AS total_size_bytes,
            COUNT(DISTINCT repo_name) AS unique_repos,
            COUNT(DISTINCT file_path) AS unique_files
        FROM code_chunks;
        """
        summary_data = await pool.fetchrow(summary_query)

        # --- Display Summary Table ---
        summary_table = Table("Metric", "Value", title="📊 Overall Database Statistics")
        if summary_data and summary_data["total_chunks"] > 0:
            summary_table.add_row("Total Chunks", str(summary_data["total_chunks"]))
            summary_table.add_row(
                "Unique Repositories", str(summary_data["unique_repos"])
            )
            summary_table.add_row("Unique Files", str(summary_data["unique_files"]))
            summary_table.add_row(
                "Average Chunk Length", f"{summary_data['avg_chunk_len']:.2f} chars"
            )
            summary_table.add_row(
                "Smallest Chunk", f"{summary_data['min_chunk_len']} chars"
            )
            summary_table.add_row(
                "Largest Chunk", f"{summary_data['max_chunk_len']} chars"
            )
            summary_table.add_row(
                "Total Size of Text", _format_bytes(summary_data["total_size_bytes"])
            )
        else:
            summary_table.add_row("Status", "Database is empty.")

        console.print(summary_table)

        # --- Fetch and Display Per-Repository Stats ---
        if summary_data and summary_data["total_chunks"] > 0:
            repo_query = "SELECT repo_name, COUNT(*) as chunk_count FROM code_chunks GROUP BY repo_name ORDER BY chunk_count DESC;"
            repo_data = await pool.fetch(repo_query)

            repo_table = Table(
                "Repository Name", "Chunk Count", title="📦 Chunks Per Repository"
            )
            for row in repo_data:
                repo_table.add_row(row["repo_name"], str(row["chunk_count"]))

            console.print(repo_table)

        await close_db_pool()

    asyncio.run(run())


@db_app.command(
    "stats",
    short_help="📊 Displays detailed statistics about the ingested data.",
    help="Prints tables with statistics about the code chunks stored in the database, including per-repository counts.",
)
def db_stats():
    _db_stats_logic()


@db_app.command("s", hidden=True)
def db_stats_alias():
    _db_stats_logic()


# ------------------------------
# --- DB Backup ---


def _db_backup_logic(outfile: Path):
    async def run():
        pool = await get_db_pool()
        rows = await pool.fetch(
            "SELECT id, file_path, chunk, embedding FROM code_chunks"
        )
        data = [dict(row) for row in rows]
        with outfile.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        await close_db_pool()
        console.print(
            f"[bold green]Backed up {len(rows)} code chunks to '{outfile}'.[/bold green]"
        )

    asyncio.run(run())


@db_app.command(
    "backup",
    short_help="dbb: Exports all code chunks to a JSON file.",
    help="Creates a backup of the [bold]code_chunks[/bold] table in JSON format. The default filename is [cyan]backup.json[/cyan].",
)
def db_backup(
    outfile: Path = typer.Argument(
        "backup.json", help="Output file path for the JSON backup."
    ),
):
    _db_backup_logic(outfile)


@db_app.command("dbb", hidden=True)
def db_backup_alias(
    outfile: Path = typer.Argument(
        "backup.json", help="Output file path for the JSON backup."
    ),
):
    _db_backup_logic(outfile)


# ------------------------------
# --- Database Clear ---


def _db_clear_logic():
    # Add a confirmation prompt for safety. abort=True exits if the user says no.
    if not typer.confirm(
        "❓ Are you sure you want to delete all ingested data? This action cannot be undone.",
        abort=True,
    ):
        return  # This line is technically not needed due to abort=True, but it's good practice.

    async def run():
        console.print("🗑️ Deleting all rows from the code_chunks table...")
        pool = await get_db_pool()
        # TRUNCATE is faster than DELETE for clearing an entire table.
        await pool.execute("TRUNCATE TABLE code_chunks RESTART IDENTITY;")
        await close_db_pool()
        console.print(
            "[bold green]All data has been successfully deleted.[/bold green]"
        )

    asyncio.run(run())


@db_app.command(
    "clear",
    short_help="dbc: Deletes all data from the database.",
    help="[bold red]DANGER:[/bold red] Removes all rows from the [bold]code_chunks[/bold] table. This action is irreversible.",
)
def db_clear():
    _db_clear_logic()


@db_app.command("dbc", hidden=True)
def db_clear_alias():
    _db_clear_logic()


# ------------------------------
# --- Ingest ---


def _ingest_logic(repo_path: Path, batch_size: int):
    from agentic.ingestor import CodeIngestor

    async def run():
        pool = await get_db_pool()
        repo_name = get_project_name(repo_path)
        console.print(
            f"Ingesting repository: [bold cyan]{repo_name}[/bold cyan] from path [dim]{repo_path}[/dim]"
        )
        ingestor = CodeIngestor(input_dir=str(repo_path), repo_name=repo_name)
        await ingestor.ingest(pool, batch_size)
        await close_db_pool()

    asyncio.run(run())


@app.command(
    "ingest",
    short_help="i: Ingests a code repository into the vector DB.",
    help="""
    Scans a directory for [bold yellow]*.py[/bold yellow] files, splits them into code-aware chunks,
    generates embeddings, and saves them to the database.

    - [bold]REPO_PATH[/bold]: The file path to the code repository to ingest.
    - [bold]--batch-size[/bold]: The number of chunks to process concurrently.
    """,
)
def ingest(
    repo_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        help="Path to the code repository to analyze.",
    ),
    batch_size: int = typer.Option(
        10, "--batch-size", "-b", help="Number of chunks to process concurrently."
    ),
):
    _ingest_logic(repo_path, batch_size)


@app.command("i", hidden=True)
def ingest_alias(
    repo_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        help="Path to the code repository to analyze.",
    ),
    batch_size: int = typer.Option(
        10, "--batch-size", "-b", help="Number of chunks to process concurrently."
    ),
):
    _ingest_logic(repo_path, batch_size)


# ------------------------------
# --- Re-Index ---
def _reindex_logic(repo_path: Path, batch_size: int):
    from agentic.ingestor import CodeIngestor

    async def run():
        pool = await get_db_pool()
        repo_name = get_project_name(repo_path)

        console.print(f"Re-indexing repository: [bold cyan]{repo_name}[/bold cyan]")

        if not typer.confirm(
            f"❓ Are you sure you want to re-index '{repo_name}'? This will delete its existing data first.",
            abort=True,
        ):
            return

        console.print(f"Deleting existing data for '{repo_name}'...")
        result = await pool.execute(
            "DELETE FROM code_chunks WHERE repo_name = $1", repo_name
        )
        console.print(f"Deleted {result.split(' ')[-1]} old records.")

        ingestor = CodeIngestor(input_dir=str(repo_path), repo_name=repo_name)
        await ingestor.ingest(pool, batch_size)

        await close_db_pool()

    asyncio.run(run())


@app.command(
    "reindex",
    short_help="ri: Re-indexes a repository by deleting and re-ingesting it.",
    help="Deletes all data associated with a specific repository name and then runs the ingestion process again for that path.",
)
def reindex(
    repo_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        help="Path to the code repository to re-index.",
    ),
    batch_size: int = typer.Option(
        10, "--batch-size", "-b", help="Number of chunks to process concurrently."
    ),
):
    _reindex_logic(repo_path, batch_size)


@app.command("ri", hidden=True)
def reindex_alias(
    repo_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        help="Path to the code repository to re-index.",
    ),
    batch_size: int = typer.Option(
        10, "--batch-size", "-b", help="Number of chunks to process concurrently."
    ),
):
    _reindex_logic(repo_path, batch_size)


# ------------------------------
# --- Query ---
def _query_logic(question: str):
    async def run():
        pool = await get_db_pool()
        agent = RAGAgent(db_pool=pool)
        console.print(f"[bold]Query:[/] {question}")
        messages = [Message(role="user", content=question)]
        result = await agent.run_rag_chat(messages)
        console.print("\n[bold]Answer:[/]")
        console.print(result)
        await close_db_pool()

    asyncio.run(run())


@app.command(
    "query",
    short_help="q: Asks a question to the RAG agent.",
    help="Runs a single query against the RAG agent. The agent will retrieve relevant code chunks and use them to generate an answer.",
)
def query(question: str):
    _query_logic(question)


@app.command("q", hidden=True)
def query_alias(question: str):
    _query_logic(question)


# ------------------------------
# --- Clear Sessions ---
def _clear_sessions_logic():
    import aioredis

    async def run():
        redis = aioredis.from_url(config.db.redis_url, decode_responses=True)
        count = 0
        async for key in redis.scan_iter("*"):
            await redis.delete(key)
            count += 1
        await redis.close()
        console.print(
            f"[bold green]Deleted {count} session keys from Redis.[/bold green]"
        )

    asyncio.run(run())


@app.command(
    "clear-sessions",
    short_help="cs: Clears all chat histories from Redis.",
    help="Deletes all keys from the Redis database, effectively clearing all persisted chat sessions and conversation histories.",
)
def clear_sessions():
    _clear_sessions_logic()


@app.command("cs", hidden=True)
def clear_sessions_alias():
    _clear_sessions_logic()


# ------------------------------
# --- Test Embedding ---
def _test_embedding_logic():
    from agentic.embeddings.ollama import get_ollama_embedding

    async def run():
        console.print(
            f"Pinging Ollama at [bold]{config.llm.ollama.embedding_url}[/]..."
        )
        try:
            emb = await get_ollama_embedding("hello world")
            console.print(
                f"[bold green]Success![/] Embedding vector received (dimension: {len(emb)})."
            )
            console.print(f"Vector preview: {emb[:5]}...")
        except Exception as e:
            console.print(f"[bold red]Error:[/] Could not get embedding. Details: {e}")

    asyncio.run(run())


@app.command(
    "embedding-test",
    short_help="et: Tests the connection to the embedding model.",
    help="Sends a test prompt to the configured Ollama embedding model to verify connectivity and configuration.",
)
def test_embedding():
    _test_embedding_logic()


@app.command("et", hidden=True)
def test_embedding_alias():
    _test_embedding_logic()


# ------------------------------
# ------------------------------

if __name__ == "__main__":
    app()
