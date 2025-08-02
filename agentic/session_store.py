import aioredis
import json
from agentic.config import Config


class SessionStore:
    def __init__(self):
        url = Config.get("redis_url", "redis://localhost:6379")
        self._redis = aioredis.from_url(url, decode_responses=True)

    async def get(self, session_id):
        data = await self._redis.get(session_id)
        return json.loads(data) if data else []

    async def set(self, session_id, messages):
        await self._redis.set(session_id, json.dumps([msg.dict() for msg in messages]), ex=3600)  # 1 hour expiry
