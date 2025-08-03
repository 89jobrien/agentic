# agentic/manage.py
import asyncio
from pathlib import Path

import typer
from rich.console import Console

from agentic.database import close_db_pool, get_db_pool
from cli.managers import AgentManager, DatabaseManager, UtilityManager

# --- Setup ---
console = Console()
app = typer.Typer(
    name="agentic",
    help="🤖 [bold]A CLI for managing the Agentic RAG codebase analyzer.[/bold]",
    rich_markup_mode="rich",
    add_completion=False,
)
db_app = typer.Typer(
    name="db",
    help="🗄️ Commands for database management (init, stats, backup, etc.)",
    rich_markup_mode="rich",
)
app.add_typer(db_app)


# --- Database ---
@db_app.command("init", short_help="🚀 Initializes the database schema and extensions.")
def db_init():
    async def run():
        pool = await get_db_pool()
        manager = DatabaseManager(pool, console)
        await manager.init()
        await close_db_pool()
    asyncio.run(run())

@db_app.command("stats", short_help="📊 Displays detailed statistics about the ingested data.")
def db_stats():
    async def run():
        pool = await get_db_pool()
        manager = DatabaseManager(pool, console)
        await manager.stats()
        await close_db_pool()
    asyncio.run(run())

@db_app.command("backup", short_help="💾 Exports all code chunks to a JSON file.")
def db_backup(outfile: Path = typer.Argument("backup.json", help="Output file path.")):
    async def run():
        pool = await get_db_pool()
        manager = DatabaseManager(pool, console)
        await manager.backup(outfile)
        await close_db_pool()
    asyncio.run(run())

@db_app.command("clear", short_help="🗑️ Deletes all data from the database.")
def db_clear():
    if not typer.confirm("❓ Are you sure you want to delete all ingested data? This action cannot be undone.", abort=True):
        return
    async def run():
        pool = await get_db_pool()
        manager = DatabaseManager(pool, console)
        await manager.clear()
        await close_db_pool()
    asyncio.run(run())


# --- Agent ---
@app.command("ingest", short_help="⚡ Ingests a code repository into the vector DB.")
def ingest(
    repo_path: Path = typer.Argument(..., help="Path to the code repository."),
    batch_size: int = typer.Option(10, "--batch-size", "-b", help="Concurrent chunks."),
):
    async def run():
        pool = await get_db_pool()
        manager = AgentManager(pool, console)
        await manager.ingest(repo_path, batch_size)
        await close_db_pool()
    asyncio.run(run())

@app.command("reindex", short_help="♻️ Re-indexes a repository.")
def reindex(
    repo_path: Path = typer.Argument(..., help="Path to the repository to re-index."),
    batch_size: int = typer.Option(10, "--batch-size", "-b", help="Concurrent chunks."),
):
    async def run():
        pool = await get_db_pool()
        manager = AgentManager(pool, console)
        await manager.reindex(repo_path, batch_size)
        await close_db_pool()
    asyncio.run(run())

@app.command("query", short_help="💬 Asks a question to the RAG agent.")
def query(question: str):
    async def run():
        pool = await get_db_pool()
        manager = AgentManager(pool, console)
        await manager.query(question)
        await close_db_pool()
    asyncio.run(run())


# --- Utility ---
@app.command("clear-sessions", short_help="🧹 Clears all chat histories from Redis.")
def clear_sessions():
    manager = UtilityManager(console)
    asyncio.run(manager.clear_sessions())

@app.command("test-embedding", short_help="🧪 Tests the connection to the embedding model.")
def test_embedding():
    manager = UtilityManager(console)
    asyncio.run(manager.test_embedding())


if __name__ == "__main__":
    app()