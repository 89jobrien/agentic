from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Response body for the chat endpoint."""
    session_id: str
    reply: str
    history: List[Message]

class ChatSession(BaseModel):
    session_id: str
    messages: List[Message]

class Embedding(BaseModel):
    vector: List[float] | None = None

class CodeChunk(BaseModel):
    file_path: str
    chunk: str
    embedding: Embedding
