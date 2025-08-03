import asyncio
import asyncpg
from pathlib import Path

from loguru import logger
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import CodeSplitter

from agentic.config import config
from agentic.utils import read_ignore_file
from agentic.embeddings.ollama import get_ollama_embedding


class CodeIngestor:
    """
    Handles loading, splitting, and ingesting code into the vector database.
    """

    def __init__(self, input_dir: str, repo_name: str):
        """
        Args:
            input_dir: The path to the code repository to ingest.
        """
        default_ignores = read_ignore_file(Path(input_dir))
        ignore_patterns = config.rag.ingestor_ignore_patterns + default_ignores
        self.repo_name = repo_name
        self.reader = SimpleDirectoryReader(
            input_dir=input_dir,
            required_exts=[".py"],
            recursive=True,
            exclude=ignore_patterns,
        )
        self.splitter = CodeSplitter(
            language=config.splitter.language,
            chunk_lines=config.splitter.chunk_size,
            chunk_lines_overlap=config.splitter.chunk_overlap,
        )
        self.nodes = None

    def load_and_split(self):
        """Loads documents and splits them into code-aware nodes."""
        logger.info(f"Loading Python files from '{self.reader.input_dir}'...")
        docs = self.reader.load_data()
        self.nodes = self.splitter.get_nodes_from_documents(docs)
        logger.success(f"Loaded and split documents into {len(self.nodes)} nodes.")
        return self.nodes

    async def _embed_and_save(self, pool: asyncpg.Pool, node):
        """Helper function to embed a single node and save it to the DB."""
        file_path = node.metadata.get("file_path", "unknown")
        code_chunk = node.get_content()

        if not code_chunk.strip():
            logger.warning(f"Skipping empty chunk from {file_path}.")
            return

        try:
            embedding = await get_ollama_embedding(code_chunk)
            await pool.execute(
                """
                INSERT INTO code_chunks (id, repo_name, file_path, chunk, embedding)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE SET
                repo_name = EXCLUDED.repo_name,
                file_path = EXCLUDED.file_path,
                chunk = EXCLUDED.chunk,
                embedding = EXCLUDED.embedding;
                """,
                node.id_,
                self.repo_name,  # Pass the repo name to the query
                file_path,
                code_chunk,
                embedding,
            )
            logger.trace(f"Successfully ingested chunk from {file_path}")
        except Exception as e:
            logger.error(f"Failed to ingest chunk from {file_path}: {e}")

    async def ingest(self, pool: asyncpg.Pool, batch_size: int = 10):
        """
        Processes all nodes in batches, generating embeddings and saving to the DB.

        Args:
            pool: The asyncpg connection pool.
            batch_size: The number of nodes to process concurrently.
        """
        if self.nodes is None:
            self.load_and_split()

        if not self.nodes:
            logger.warning("No nodes found to ingest.")
            return

        logger.info(f"Ingesting {len(self.nodes)} nodes in batches of {batch_size}...")
        tasks = []
        for node in self.nodes:
            tasks.append(self._embed_and_save(pool, node))
            if len(tasks) >= batch_size:
                await asyncio.gather(*tasks)
                tasks = []

        if tasks:  # Process any remaining tasks
            await asyncio.gather(*tasks)

        logger.success("Ingestion complete.")


# import asyncio
# import asyncpg
# import httpx
# import json
# import uuid
# from llama_index.core import SimpleDirectoryReader
# from llama_index.core.node_parser import CodeSplitter
# from agentic.config import config


# class CodeIngestor:
#     def __init__(
#         self,
#         input_dir=".",
#         database_url=config.db.database_url,
#         embed_url=config.llm.ollama_url,
#         chunk_lines=40,
#         chunk_lines_overlap=5
#     ):
#         self.reader = SimpleDirectoryReader(input_dir=input_dir, required_exts=[".py"])
#         self.splitter = CodeSplitter(
#             language="python",
#             chunk_lines=chunk_lines,
#             chunk_lines_overlap=chunk_lines_overlap
#         )
#         self.database_url = database_url
#         self.embed_url = embed_url
#         self.nodes = None

#     def load_and_split(self):
#         docs = self.reader.load_data()
#         self.nodes = self.splitter.get_nodes_from_documents(docs)
#         return self.nodes

#     async def fetch_embedding(self, texts):
#         async with httpx.AsyncClient() as client:
#             for text in texts:
#                 resp = await client.post(
#                     self.embed_url,
#                     json={"model": "nomic-embed-text", "prompt": text}
#                 )
#                 resp.raise_for_status()
#                 data = resp.json()
#                 return data["embedding"]

#     async def save_to_db(self, pool, node, embedding):
#         file_path = node.metadata.get("file_path") or "unknown"
#         emb_str = f"{embedding}"
#         try:
#             await pool.execute(
#                 """
#                 INSERT INTO code_chunks (id, file_path, chunk, embedding)
#                 VALUES ($1, $2, $3, $4)
#                 """,
#                 node.id_,
#                 file_path,
#                 node.get_content(),
#                 emb_str,
#             )
#         except Exception as e:
#             print(f"[DB ERROR in save_to_db] {e}")

#     async def _embed_and_save(self, pool, node):
#         try:
#             print(f"Inserting: id={node.id_}, file_path={node.metadata.get('file_path')}")
#             code_chunk = node.get_content()
#             print(f"Chunk: {code_chunk[:60]!r}...")
#             embedding = await self.fetch_embedding(code_chunk)
#             print(f"Embedding type: {type(embedding)}, value preview: {str(embedding)[:60]}...")
#             await self.save_to_db(pool, node, embedding)
#         except Exception as e:
#             print(f"[ERROR in _embed_and_save] {e}")

#     async def ingest(self, batch_size=10):
#         if self.nodes is None:
#             self.load_and_split()

#         pool = await asyncpg.create_pool(self.database_url)

#         try:
#             tasks = []
#             if self.nodes:
#                 for node in self.nodes:
#                     if not node.get_content():
#                         continue

#                     tasks.append(self._embed_and_save(pool, node))

#                     if len(tasks) >= batch_size:
#                         results = await asyncio.gather(*tasks, return_exceptions=True)
#                         for result in results:
#                             if isinstance(result, Exception):
#                                 print(f"[TASK ERROR] {result}")
#                         tasks = []
#                 if tasks:
#                     results = await asyncio.gather(*tasks, return_exceptions=True)
#                     for result in results:
#                         if isinstance(result, Exception):
#                             print(f"[TASK ERROR] {result}")

#         finally:
#             await pool.close()
