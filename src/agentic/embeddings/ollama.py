from src.agentic.config import config
import httpx


async def get_ollama_embedding(text: str) -> list[float]:
    url = config.llm.ollama.embedding_url
    if not url:
        raise ValueError("Ollama URL is missing in configuration.")
    model = config.llm.ollama.embedder_model
    if not model:
        raise ValueError("Ollama model is missing in configuration.")
    async with httpx.AsyncClient(timeout=config.llm.request_timeout) as client:
        response = await client.post(url, json={"model": model, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]
