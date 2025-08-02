import asyncio
from agentic.database import get_db_pool


async def migrate():
    pool = await get_db_pool()
    await pool.execute("""
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE IF NOT EXISTS code_chunks (
        id SERIAL PRIMARY KEY,
        file_path TEXT,
        chunk TEXT,
        embedding vector(768)
    );
    CREATE INDEX IF NOT EXISTS code_chunks_embedding_idx ON code_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    """)
    await pool.close()


if __name__ == "__main__":
    asyncio.run(migrate())
