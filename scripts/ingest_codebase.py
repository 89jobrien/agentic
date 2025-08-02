import asyncio
from agentic.ingest import get_code_chunks
from agentic.embeddings.ollama import get_ollama_embedding
from agentic.database import get_db_pool

async def ingest_repo(repo_path: str):
    pool = await get_db_pool()
    async for chunk_info in get_chunks_with_embedding(repo_path):
        await pool.execute(
            "INSERT INTO code_chunks (file_path, chunk, embedding) VALUES ($1, $2, $3)",
            chunk_info["file_path"],
            chunk_info["chunk"],
            chunk_info["embedding"]
        )
    await pool.close()

async def get_chunks_with_embedding(repo_path):
    # This generator yields chunk dicts with an added 'embedding'
    for chunk in get_code_chunks(repo_path):
        embedding = await get_ollama_embedding(chunk["chunk"])
        chunk["embedding"] = embedding
        yield chunk

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python ingest_codebase.py /path/to/repo")
        exit(1)
    asyncio.run(ingest_repo(sys.argv[1]))