# import asyncio
# from agentic.ingest import get_code_chunks
# from agentic.embeddings.ollama import get_ollama_embedding
# from agentic.database import get_db_pool
# from loguru import logger
# from tqdm import tqdm

# async def ingest_repo(repo_path: str):
#     pool = await get_db_pool()
#     print("Collecting code chunks...")
#     chunks = list(get_code_chunks(repo_path))
#     print(f"Found {len(chunks)} code chunks.")
#     for chunk in tqdm(chunks, desc="Embedding and ingesting"):
#         if not str(chunk["chunk"]).strip():
#             print(f"Skipping empty chunk in {chunk['file_path']}")
#             continue
#         if len(chunk["chunk"]) > 10000:
#             print(f"Skipping giant chunk in {chunk['file_path']} (size={len(chunk['chunk'])})")
#             continue
#         print(f"[DEBUG] About to embed: {chunk['file_path']} (len={len(chunk['chunk'])})")
#         try:
#             embedding = await get_ollama_embedding(chunk["chunk"])
#             print(f"[DEBUG] Got embedding for {chunk['file_path']}")
#         except Exception as e:
#             print(f"EMBEDDING FAILED for {chunk['file_path']}: {e}")
#             continue  # optionally skip or handle error
#         print(f"[DEBUG] Inserting {chunk['file_path']} into DB")
#         # (insert into DB here)
#         print(f"[DEBUG] Inserted {chunk['file_path']} into DB")
#         # Convert embedding to vector string for pgvector (see previous responses)
#         embedding_str = f"({', '.join(str(x) for x in embedding)})"
#         print(f"[DEBUG] Inserting {chunk['file_path']} into DB")
#         await pool.execute(
#             "INSERT INTO code_chunks (file_path, chunk, embedding) VALUES ($1, $2, $3::vector)",
#             chunk["file_path"],
#             chunk["chunk"],
#             embedding_str
#         )
#         print(f"[DEBUG] Inserted {chunk['file_path']}")
#     await pool.close()
#     print("Ingestion complete.")

# # async def get_chunks_with_embedding(repo_path):
# #     chunks = list(get_code_chunks(repo_path))
# #     for chunk in tqdm(chunks, desc="Embedding and ingesting"):
# #         embedding = await get_ollama_embedding(chunk["chunk"])
# #         chunk["embedding"] = embedding
# #         yield chunk

# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) != 2:
#         print("Usage: python ingest_codebase.py /path/to/repo")
#         exit(1)
#     asyncio.run(ingest_repo(sys.argv[1]))
