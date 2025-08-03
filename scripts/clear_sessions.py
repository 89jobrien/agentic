import asyncio
from agentic.config import Config
import aioredis


async def clear_sessions():
    redis_url = Config.get("redis_url")
    if not redis_url:
        print("No redis_url found in config.")
        return

    redis = aioredis.from_url(redis_url, decode_responses=True)
    count = 0
    async for key in redis.scan_iter("*"):
        await redis.delete(key)
        count += 1
    print(f"Deleted {count} session keys.")


if __name__ == "__main__":
    asyncio.run(clear_sessions())
