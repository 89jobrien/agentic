from agentic.config import Config
import httpx


async def azure_chat(messages: list[dict], temperature: float = 0.0) -> str:
    base = Config.get("azure_openai_endpoint")
    api_key = Config.get("azure_openai_api_key")
    api_version = Config.get("azure_openai_api_version")
    deployment = Config.get("azure_openai_chat_deployment")
    url = f"{base}openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"messages": messages, "temperature": temperature},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
