import asyncio
import typer
from pathlib import Path
from datetime import datetime

app = typer.Typer()

@app.command()
def ingest(repo_path: str):
    """
    Ingest a repository and add its code chunks/embeddings to the database.
    """
    from agentic.ingest import get_code_chunks
    from agentic.embeddings.ollama import get_ollama_embedding
    from agentic.database import get_db_pool

    async def run():
        pool = await get_db_pool()
        for chunk in get_code_chunks(repo_path):
            embedding = await get_ollama_embedding(chunk["chunk"])
            await pool.execute(
                "INSERT INTO code_chunks (file_path, chunk, embedding) VALUES ($1, $2, $3)",
                chunk["file_path"], chunk["chunk"], embedding
            )
        await pool.close()
        print("Ingestion complete.")

    asyncio.run(run())

@app.command()
def clear_sessions():
    """
    Remove all session keys from Redis (clears chat context/history).
    """
    import aioredis
    from agentic.config import Config

    async def run():
        redis_url = Config.get("redis_url")
        redis = aioredis.from_url(redis_url, decode_responses=True)
        count = 0
        async for key in redis.scan_iter("*"):
            await redis.delete(key)
            count += 1
        print(f"Deleted {count} session keys.")
    asyncio.run(run())

@app.command()
def test_query(question: str):
    """
    Run a test analysis query against the loaded codebase.
    """
    from agentic.rag_agent import run_rag_query

    async def run():
        result = await run_rag_query(question)
        print("---- Result ----\n", result)
    asyncio.run(run())

@app.command()
def reindex():
    """
    Rebuild or re-insert embeddings for all code chunks in DB.
    """
    from agentic.ingest import get_code_chunks
    from agentic.embeddings.ollama import get_ollama_embedding
    from agentic.database import get_db_pool

    async def run():
        pool = await get_db_pool()
        await pool.execute("DELETE FROM code_chunks")
        # Update the path below as needed for your codebase root
        repo_path = typer.prompt("Enter repository path for reindexing")
        for chunk in get_code_chunks(repo_path):
            embedding = await get_ollama_embedding(chunk["chunk"])
            await pool.execute(
                "INSERT INTO code_chunks (file_path, chunk, embedding) VALUES ($1, $2, $3)",
                chunk["file_path"], chunk["chunk"], embedding
            )
        await pool.close()
        print("Reindex complete.")
    asyncio.run(run())

@app.command()
def stats():
    """
    Print statistics about the code_chunks table.
    """
    from agentic.database import get_db_pool

    async def run():
        pool = await get_db_pool()
        count = await pool.fetchval("SELECT COUNT(*) FROM code_chunks")
        avg_len = await pool.fetchval("SELECT AVG(LENGTH(chunk)) FROM code_chunks")
        print(f"Total chunks: {count}")
        print(f"Average chunk length: {avg_len:.2f}")
        await pool.close()
    asyncio.run(run())

@app.command()
def backup(outfile: str = typer.Argument(f"code_chunks_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")):
    """
    Export all code chunks to a JSON file for backup/portability.
    """
    import json
    from agentic.database import get_db_pool

    async def run():
        pool = await get_db_pool()
        rows = await pool.fetch("SELECT file_path, chunk, embedding FROM code_chunks")
        with open(outfile, 'w', encoding='utf-8') as f:
            # Convert asyncpg Records to dict (embedding might be a vector type)
            out = [{
                "file_path": row["file_path"],
                "chunk": row["chunk"],
                "embedding": list(row["embedding"]) if not isinstance(row["embedding"], list) else row["embedding"]
            } for row in rows]
            json.dump(out, f, ensure_ascii=False, indent=2)
        await pool.close()
        print(f"Backed up {len(rows)} code chunks to {outfile}")

    asyncio.run(run())

@app.command()
def restore(infile: str):
    """
    Import code chunks from a backup JSON into the database.
    """
    import json
    from agentic.database import get_db_pool

    async def run():
        with open(infile, 'r', encoding='utf-8') as f:
            data = json.load(f)
        pool = await get_db_pool()
        await pool.execute("DELETE FROM code_chunks")  # Optional: clear before restore
        for row in data:
            await pool.execute(
                "INSERT INTO code_chunks (file_path, chunk, embedding) VALUES ($1, $2, $3)",
                row["file_path"], row["chunk"], row["embedding"]
            )
        await pool.close()
        print(f"Restored {len(data)} code chunks from {infile}")

    asyncio.run(run())

@app.command()
def preview(n: int = typer.Option(5, help="Number of code chunks to preview")):
    """
    Show a sample of code chunks from the database.
    """
    from agentic.database import get_db_pool

    async def run():
        pool = await get_db_pool()
        rows = await pool.fetch("SELECT file_path, LEFT(chunk,200) as snippet FROM code_chunks LIMIT $1", n)
        for i, row in enumerate(rows, 1):
            print(f"--- Chunk {i} ---\nPath: {row['file_path']}\nSnippet:\n{row['snippet']}\n")
        await pool.close()
    asyncio.run(run())

@app.command()
def tail_log(logfile: str = typer.Option("agentic.log", help="Log file to tail")):
    """
    Tail the specified Agentic log file in real time.
    """
    import time

    if not Path(logfile).exists():
        print(f"Log file {logfile} does not exist. Make sure logging is enabled to file in agentic/logging.py")
        raise typer.Exit(1)
    print(f"Tailing log {logfile} (Ctrl+C to exit):")
    with open(logfile, "r") as f:
        # Go to end of file
        f.seek(0, 2)
        try:
            while True:
                line = f.readline()
                if line:
                    print(line, end="")
                else:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopped log tailing.")

@app.command()
def backup_with_stats(outfile: str = typer.Argument(
        f"code_chunks_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    )):
    """
    Export all code chunks to a JSON file with summary statistics.
    """
    import json
    from agentic.database import get_db_pool

    async def run():
        pool = await get_db_pool()
        rows = await pool.fetch("SELECT file_path, chunk, embedding FROM code_chunks")
        
        # Build export data
        out_chunks = [{
            "file_path": row["file_path"],
            "chunk": row["chunk"],
            "embedding": list(row["embedding"]) if not isinstance(row["embedding"], list) else row["embedding"]
        } for row in rows]

        total_chunks = len(out_chunks)
        avg_length = (
            sum(len(chunk["chunk"]) for chunk in out_chunks) / total_chunks
            if total_chunks else 0
        )
        
        # Optional: stats by file
        from collections import defaultdict
        file_counts = defaultdict(int)
        for chunk in out_chunks:
            file_counts[chunk["file_path"]] += 1

        summary = {
            "total_chunks": total_chunks,
            "average_chunk_length": avg_length,
            "chunks_per_file": dict(file_counts),
        }

        export = {
            "summary": summary,
            "chunks": out_chunks
        }

        with open(outfile, 'w', encoding='utf-8') as f:
            json.dump(export, f, ensure_ascii=False, indent=2)
        await pool.close()

        print(f"Backed up {total_chunks} code chunks (+ stats) to {outfile}")
        print(f"Average chunk length: {avg_length:.1f}")
        print(f"Example file chunk counts: {dict(list(file_counts.items())[:5])}")

    asyncio.run(run())

if __name__ == "__main__":
    app()