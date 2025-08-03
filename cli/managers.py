# agentic/managers.py
import asyncio
import json
from pathlib import Path

import redis.asyncio as redis
import asyncpg
import typer

from rich.console import Console
from rich.table import Table
from rich.progress import Progress


from agentic.config import config
from agentic.embeddings.ollama import get_ollama_embedding
from agentic.ingestor import CodeIngestor
from agentic.models import Message
from agentic.rag_agent import RAGAgent
from agentic.utils import get_project_name
from agentic.formatting import writer
from agentic.formatting.console import console

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


class DatabaseManager:
    """Manages all direct database operations for the CLI."""

    def __init__(self, pool: asyncpg.Pool, console: Console):
        self.pool = pool
        self.console = console

    async def init(self):
        self.console.print("Creating 'vector' extension if it doesn't exist...")
        await self.pool.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        self.console.print("Creating 'code_chunks' table if it doesn't exist...")
        await self.pool.execute(
            f"""
        CREATE TABLE IF NOT EXISTS code_chunks (
            id TEXT PRIMARY KEY,
            repo_name TEXT,
            file_path TEXT,
            chunk TEXT,
            embedding vector({config.llm.embedding_dim})
        );
        """
        )
        self.console.print("Creating IVF flat index on embeddings...")
        await self.pool.execute(
            """
        CREATE INDEX IF NOT EXISTS code_chunks_embedding_idx
        ON code_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        """
        )
        self.console.print("[bold green]Database initialization complete.[/bold green]")

    async def stats(self):
        summary_query = """
        SELECT
            COUNT(*) AS total_chunks, AVG(LENGTH(chunk)) AS avg_chunk_len,
            MIN(LENGTH(chunk)) AS min_chunk_len, MAX(LENGTH(chunk)) AS max_chunk_len,
            SUM(LENGTH(chunk)) AS total_size_bytes, COUNT(DISTINCT repo_name) AS unique_repos,
            COUNT(DISTINCT file_path) AS unique_files
        FROM code_chunks;
        """
        summary_data = await self.pool.fetchrow(summary_query)

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

        if summary_data and summary_data["total_chunks"] > 0:
            repo_query = "SELECT repo_name, COUNT(*) as chunk_count FROM code_chunks GROUP BY repo_name ORDER BY chunk_count DESC;"
            repo_data = await self.pool.fetch(repo_query)
            repo_table = Table(
                "Repository Name", "Chunk Count", title="📦 Chunks Per Repository"
            )
            for row in repo_data:
                repo_table.add_row(row["repo_name"], str(row["chunk_count"]))
            console.print(repo_table)

    async def backup(self, outfile: Path):
        rows = await self.pool.fetch(
            "SELECT id, repo_name, file_path, chunk, embedding FROM code_chunks"
        )
        data = [dict(row) for row in rows]
        with outfile.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.console.print(
            f"[bold green]Backed up {len(rows)} code chunks to '{outfile}'.[/bold green]"
        )

    async def clear(self):
        self.console.print("🗑️ Deleting all rows from the code_chunks table...")
        await self.pool.execute("TRUNCATE TABLE code_chunks RESTART IDENTITY;")
        self.console.print(
            "[bold green]All data has been successfully deleted.[/bold green]"
        )


class AgentManager:
    """Manages high-level agent tasks like ingestion and querying."""

    def __init__(self, pool: asyncpg.Pool, console: Console):
        self.pool = pool
        self.console = console

    async def ingest(self, repo_path: Path, batch_size: int):
        repo_name = get_project_name(repo_path)
        self.console.print(
            f"Ingesting repository: [bold cyan]{repo_name}[/bold cyan] from path [dim]{repo_path}[/dim]"
        )
        ingestor = CodeIngestor(input_dir=str(repo_path), repo_name=repo_name)
        nodes = ingestor.load_and_split()
        with Progress(console=self.console) as progress:
            task = progress.add_task("[green]Ingesting chunks...", total=len(nodes))
            
            async def ingest_node(node):
                await ingestor._embed_and_save(self.pool, node)
                progress.update(task, advance=1)

            tasks = [ingest_node(node) for node in nodes]
            await asyncio.gather(*tasks)

    async def reindex(self, repo_path: Path, batch_size: int):
        repo_name = get_project_name(repo_path)
        self.console.print(f"Re-indexing repository: [bold cyan]{repo_name}[/bold cyan]")
        if not typer.confirm(
            f"❓ Are you sure you want to re-index '{repo_name}'? This will delete its existing data first.",
            abort=True,
        ):
            return
        self.console.print(f"Deleting existing data for '{repo_name}'...")
        result = await self.pool.execute(
            "DELETE FROM code_chunks WHERE repo_name = $1", repo_name
        )
        self.console.print(f"Deleted {result.split(' ')[-1]} old records.")
        await self.ingest(repo_path, batch_size)

    async def query(self, question: str):
        agent = RAGAgent(db_pool=self.pool)
        self.console.print(f"[bold]Query:[/] {question}")
        with self.console.status("[bold cyan]Thinking...", spinner="dots"):
            messages = [Message(role="user", content=question)]
            result = await agent.run_rag_chat(messages)

        writer.write("\nAnswer:")
        writer.aiwrite(result)


class UtilityManager:
    """Manages miscellaneous utility and diagnostic commands."""

    def __init__(self, console: Console):
        self.console = console

    async def clear_sessions(self):
        client = redis.from_url(config.db.redis_url, decode_responses=True)
        count = 0
        async for key in client.scan_iter("*"):
            await client.delete(key)
            count += 1
        await client.close()
        writer.write(
            f"[bold green]Deleted {count} session keys from Redis.[/bold green]"
        )

    async def test_embedding(self):
        self.console.print(
            f"Pinging Ollama at [bold]{config.llm.ollama.embedding_url}[/]..."
        )
        try:
            emb = await get_ollama_embedding("hello world")
            self.console.print(
                f"[bold green]Success![/] Embedding vector received (dimension: {len(emb)})."
            )
            self.console.print(f"Vector preview: {emb[:5]}...")
        except Exception as e:
            self.console.print(f"[bold red]Error:[/] Could not get embedding. Details: {e}")