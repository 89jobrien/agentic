import redis.asyncio as aioredis
import json
from src.agentic.models import Message


class SessionStore:
    """
    Manages chat session storage in Redis.

    This class handles getting and setting chat messages for a given session_id,
    persisting the data in a Redis database.
    """

    def __init__(self, redis_url: str):
        """
        Initializes the Redis connection.

        Args:
            redis_url: The connection string for the Redis instance.
        """
        # from_url is the recommended way to create a client instance.
        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    async def get(self, session_id: str) -> list[Message]:
        """
        Retrieves chat messages for a given session ID.

        Args:
            session_id: The unique identifier for the chat session.

        Returns:
            A list of Message objects, or an empty list if the session is not found.
        """
        data = await self._redis.get(session_id)
        if not data:
            return []

        # Deserialize the JSON data back into a list of Message objects
        messages_data = json.loads(data)
        return [Message(**msg_data) for msg_data in messages_data]

    async def set(self, session_id: str, messages: list[Message]):
        """
        Saves chat messages for a session ID with a 1-hour expiry.

        Args:
            session_id: The unique identifier for the chat session.
            messages: A list of Message objects to save.
        """
        # Use model_dump() for Pydantic v2 instead of the deprecated dict()
        messages_as_dict = [msg.model_dump() for msg in messages]
        await self._redis.set(
            session_id, json.dumps(messages_as_dict), ex=3600
        )  # 1 hour expiry

    async def close(self):
        """Closes the Redis connection pool."""
        await self._redis.close()
