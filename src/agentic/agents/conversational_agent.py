from src.agentic.models import Message
from src.agentic.config import AppConfig, config as default_config
from src.agentic.chat.azure import azure_chat

class ConversationalAgent:
    """
    A conversational agent using Azure OpenAI's chat API (no retrieval).
    """

    def __init__(self, config_obj: AppConfig = default_config):
        self.config = config_obj

    async def run_chat(self, messages: list[Message]) -> str:
        """
        Conducts a chat turn using Azure OpenAI (no RAG).

        Args:
            messages: The history of the conversation.

        Returns:
            The assistant's generated reply.
        """
        if not messages or messages[-1].role != "user":
            return "Please provide a user message."

        # Optionally prepend a system prompt
        formatted_messages = []
        if self.config.rag.system_prompt:
            formatted_messages.append({"role": "system", "content": self.config.rag.system_prompt})
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        reply = await azure_chat(formatted_messages, temperature=self.config.llm.temperature)
        return reply
