from agentic.config import Config
import httpx

async def get_ollama_embedding(text: str) -> list[float]:
    url = Config.get("ollama_url")
    if not url:
        raise ValueError("Ollama URL is missing in configuration.")
    model = Config.get("ollama_model")
    if not model:
        raise ValueError("Ollama model is missing in configuration.")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"model": model, "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]