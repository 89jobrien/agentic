import asyncpg
from typing import Optional
from loguru import logger

from agentic.embeddings.ollama import get_ollama_embedding
from agentic.models import Message
from agentic.config import AppConfig, config as default_config
from agentic.chat.azure import azure_chat


class RAGAgent:
    """
    A Retrieval-Augmented Generation agent for code analysis.
    It retrieves relevant code chunks from a database and uses them
    to inform an LLM to answer questions.
    """

    def __init__(self, db_pool: asyncpg.Pool, config_obj: AppConfig = default_config):
        """
        Initializes the RAGAgent.

        Args:
            db_pool: An initialized asyncpg database connection pool.
            config_obj: The application configuration object.
        """
        self.db_pool = db_pool
        self.config = config_obj

    async def retrieve_code_chunks(
        self, search_query: str, repo_name: Optional[str] = None
    ) -> str:
        """
        Finds and returns the most relevant code chunks based on a search query.

        Args:
            search_query: The user's question or query.

        Returns:
            A string containing the concatenated relevant code chunks.
        """
        embedding = await get_ollama_embedding(search_query)

        if repo_name:
            logger.info(f"Retrieving chunks for query in repo: '{repo_name}'")
            rows = await self.db_pool.fetch(
                "SELECT file_path, chunk FROM code_chunks WHERE repo_name = $3 ORDER BY embedding <-> $1 LIMIT $2",
                embedding,
                self.config.llm.retriever_top_k,
                repo_name,
            )
        else:
            logger.info("Retrieving chunks for query across all repos.")
            rows = await self.db_pool.fetch(
                "SELECT file_path, chunk FROM code_chunks ORDER BY embedding <-> $1 LIMIT $2",
                embedding,
                self.config.llm.retriever_top_k,
            )

        if not rows:
            logger.warning(f"No code chunks found for query: '{search_query}'")
            return "No relevant code chunks were found."

        return "\n\n".join(
            [f"File: {row['file_path']}\n---\n{row['chunk']}" for row in rows]
        )

    async def run_rag_chat(self, messages: list[Message]) -> str:
        """
        Conducts a RAG-powered chat turn.

        It retrieves context based on the latest user message and injects it
        into the prompt for the Azure OpenAI model.

        Args:
            messages: The history of the conversation.

        Returns:
            The assistant's generated reply.
        """
        if not messages or messages[-1].role != "user":
            return "Please provide a user message."

        last_user_message = messages[-1].content
        logger.info(f"Retrieving context for: '{last_user_message}'")

        # 1. Retrieve context
        retrieved_context = await self.retrieve_code_chunks(last_user_message)

        # 2. Construct a new system prompt including the retrieved context
        contextual_system_prompt = f"""
{self.config.rag.system_prompt}

Here is some relevant code context from the codebase. Use this to inform your answer:
---
{retrieved_context}
---
"""

        # 3. Format messages for the API
        # We replace the original system prompt with our new contextual one
        formatted_messages = [{"role": "system", "content": contextual_system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        logger.info("Sending request to Azure OpenAI...")
        reply = await azure_chat(formatted_messages)
        return reply


# import asyncio

# from dataclasses import dataclass
# from pydantic_ai import Agent, RunContext
# from agentic.embeddings.ollama import get_ollama_embedding
# from agentic.database import get_db_pool
# from agentic.models import Message
# import asyncpg
# from agentic.chat.azure import azure_chat
# from agentic.ingestor import CodeIngestor
# from agentic.config import config
# from loguru import logger

# @dataclass
# class Deps:
#     pool: asyncpg.Pool


# class RAGAgent():
#     def __init__(self, config_obj = config, db_pool=None):
#         self.ingestor = CodeIngestor()
#         self.db_pool = db_pool
#         self.config = config_obj
#         self.rag_agent = Agent(
#             model = self.config.rag.model,
#             system_prompt = self.config.rag.system_prompt,
#             # model="openai:gpt-4o",
#             deps_type=Deps,
#             # system_prompt="You are an AI agent that analyzes and improves code based on retrieved code chunks.",
#             )

#     # def __repr__(self):
#     #     return f"{self.__str__()}()"

#     async def retrieve_code_chunks(self, search_query: str, top_k: int = 8) -> str:
#         embedding = await get_ollama_embedding(search_query)
#         embedding_str = [float(x) for x in embedding]
#         if self.db_pool is None:
#             self.db_pool = await get_db_pool()
#         rows = await self.db_pool.fetch(
#             "SELECT file_path, chunk FROM code_chunks ORDER BY embedding <-> $1 LIMIT $2",
#             embedding_str, top_k,
#     )
#         return "\n\n".join([f"{row['file_path']}:\n{row['chunk']}" for row in rows])

#     async def run_rag_query(self, question: str, top_k: int = 8) -> str:
#         result = await self.retrieve_code_chunks(question, top_k)
#         return result

#     async def run_rag_chat(self, messages: list[Message]):
#         if self.db_pool is None:
#             self.db_pool = await get_db_pool()
#             prompt = (
#                 "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in messages])
#                 + "\nAssistant:"
#             )
#             formatted_msgs = [{"role": msg.role + prompt, "content": msg.content} for msg in messages]
#             reply = await azure_chat(formatted_msgs)
#             return reply

#     async def ingest_codebase(self, batch_size: int = 10):
#         await self.ingestor.ingest(batch_size=batch_size)
