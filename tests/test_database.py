import pytest
from src.agentic.database import get_db_pool, close_db_pool

@pytest.mark.asyncio
async def test_get_db_pool_creates_and_closes(patch_db_pool):
    pool = await get_db_pool()
    assert pool is not None
    await close_db_pool()
