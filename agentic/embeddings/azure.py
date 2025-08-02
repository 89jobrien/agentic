# # agentic/azure_embedder.py
# from agentic.config import Config
# import httpx


# async def get_azure_embedding(text: str) -> list[float]:
#     base = Config.get("azure_openai_endpoint")
#     api_key = Config.get("azure_openai_api_key")
#     api_version = Config.get("azure_openai_api_version")
#     deployment = Config.get("azure_openai_embedding_deployment")
#     url = f"{base}openai/deployments/{deployment}/embeddings?api-version={api_version}"
#     headers = {"api-key": api_key, "Content-Type": "application/json"}
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, json={"input": text}, headers=headers)
#         response.raise_for_status()
#         return response.json()["data"][0]["embedding"]
