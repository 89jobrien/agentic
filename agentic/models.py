from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatSession(BaseModel):
    session_id: str
    messages: List[Message]


class CodeChunk(BaseModel):
    file_path: str
    chunk: str
