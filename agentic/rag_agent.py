from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from agentic.embeddings.ollama import get_ollama_embedding
from agentic.database import get_db_pool
from agentic.models import Message
import asyncpg
from agentic.chat.azure import azure_chat


@dataclass
class Deps:
    pool: asyncpg.Pool


agent = Agent(
    model="openai:gpt-4o",
    deps_type=Deps,
    system_prompt="You are an AI agent that analyzes and improves code based on retrieved code chunks.",
)


@agent.tool
async def retrieve_code_chunks(
    ctx: RunContext[Deps], search_query: str, top_k: int
) -> str:
    embedding = await get_ollama_embedding(search_query)
    rows = await ctx.deps.pool.fetch(
        "SELECT file_path, chunk FROM code_chunks ORDER BY embedding <-> $1 LIMIT 8",
        embedding,
        top_k,
    )
    return "\n\n".join([f"{row['file_path']}:\n{row['chunk']}" for row in rows])


async def run_rag_query(question: str) -> str:
    pool = await get_db_pool()
    embedding = await get_ollama_embedding(question)
    rows = await pool.fetch(
        "SELECT file_path, chunk FROM code_chunks ORDER BY embedding <-> $1 LIMIT 8",
        embedding,
    )
    # Format or summarize retrieved info as needed
    retrieved = "\n\n".join([f"{row['file_path']}:\n{row['chunk']}" for row in rows])
    # You may want to add LLM summary here if desired
    return retrieved


async def run_rag_chat(messages: list[Message]) -> str:
    pool = await get_db_pool()
    deps = Deps(pool=pool)
    prompt = (
        "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in messages])
        + "\nAssistant:"
    )
    formatted_msgs = [{"role": msg.role, "content": msg.content} for msg in messages]
    reply = await azure_chat(formatted_msgs)
    return reply
