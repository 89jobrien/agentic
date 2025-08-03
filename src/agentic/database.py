from agentic.config import config
import asyncpg
import pgvector.asyncpg


_db_pool = None


async def init_vector_codec(conn):
    """
    An initializer function that is run on every new database connection.
    It registers the pgvector type handler so that Python lists are
    correctly translated to and from PostgreSQL vector types.
    """
    await pgvector.asyncpg.register_vector(conn)


async def get_db_pool():
    """
    Gets the existing database connection pool, or creates it if it doesn't exist.
    """
    global _db_pool
    if _db_pool is None:
        database_url = config.db.database_url
        _db_pool = await asyncpg.create_pool(dsn=database_url, init=init_vector_codec)
    return _db_pool


async def close_db_pool():
    """
    Closes the database connection pool if it exists.
    """
    global _db_pool
    if _db_pool is not None:
        await _db_pool.close()
        _db_pool = None
