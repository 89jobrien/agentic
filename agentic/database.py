from agentic.config import Config
import asyncpg

_db_pool = None

async def get_db_pool():
    global _db_pool
    if _db_pool is None:
        db_url = Config.get("database_url")
        _db_pool = await asyncpg.create_pool(db_url)
    return _db_pool

async def close_db_pool():
    global _db_pool
    if _db_pool is not None:
        await _db_pool.close()
        _db_pool = None