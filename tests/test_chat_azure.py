import pytest
from src.agentic.chat.azure import azure_chat

@pytest.mark.asyncio
async def test_azure_chat(patch_azure_chat):
    reply = await azure_chat([{"role": "user", "content": "hi"}])
    assert reply == "Test Azure reply"
