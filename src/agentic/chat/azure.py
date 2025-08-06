import httpx
from src.agentic.config import config


async def azure_chat(messages: list[dict], temperature: float = 0.0) -> str:
    """
    Sends a chat completion request to the Azure OpenAI service.

    Args:
        messages: A list of message dictionaries for the chat.
        llm_config: The LLM configuration object containing endpoint details.
        temperature: The sampling temperature for the model.

    Returns:
        The content of the assistant's reply.
    """
    url = (
        f"{config.llm.azure.endpoint}openai/deployments/"
        f"{config.llm.azure.chat_deployment}/chat/completions"
        f"?api-version={config.llm.azure.api_version}"
    )
    headers = {
        "api-key": config.llm.azure.api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=config.llm.request_timeout) as client:
        response = await client.post(
            url,
            json={"messages": messages, "temperature": temperature},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
