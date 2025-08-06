import pytest
from src.agentic.conversational_agent import ConversationalAgent
from src.agentic.models import Message

from tests.conftest import patch_azure_chat

@pytest.mark.asyncio
async def test_conversational_agent_run_chat(patch_azure_chat, patch_config):
    agent = ConversationalAgent()
    messages = [Message(role="user", content="Hi")]
    reply = await agent.run_chat(messages)
    assert reply == "Test Azure reply"

@pytest.mark.asyncio
async def test_conversational_agent_no_user_message(patch_config):
    agent = ConversationalAgent()
    messages = []
    result = await agent.run_chat(messages)
    assert "Please provide a user message." in result
