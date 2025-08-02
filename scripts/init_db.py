# scripts/init_db.py
import asyncio
from agentic.database import get_db_pool


async def main():
    pool = await get_db_pool()
    await pool.execute("""
    CREATE TABLE IF NOT EXISTS code_chunks (
        id SERIAL PRIMARY KEY,
        file_path TEXT,
        chunk TEXT,
        embedding VECTOR(768)
    );
    """)
    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
