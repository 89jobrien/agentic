import pytest
from src.agentic.ingestor import CodeIngestor

def test_code_ingestor_load_and_split(tmp_path, patch_config):
    # Create a dummy .py file
    code_dir = tmp_path / "repo"
    code_dir.mkdir()
    (code_dir / "a.py").write_text("def foo():\n    pass\n")
    ingestor = CodeIngestor(str(code_dir), repo_name="repo")
    nodes = ingestor.load_and_split()
    assert isinstance(nodes, list)
    assert len(nodes) > 0

@pytest.mark.asyncio
async def test_code_ingestor_ingest(monkeypatch, tmp_path, patch_ollama_embedding, patch_config, mock_db_pool):
    # Patch splitter and nodes
    code_dir = tmp_path / "repo"
    code_dir.mkdir()
    (code_dir / "a.py").write_text("def foo():\n    pass\n")
    ingestor = CodeIngestor(str(code_dir), repo_name="repo")
    ingestor.load_and_split()
    # Patch _embed_and_save to just count calls
    called = []
    async def fake_embed_and_save(pool, node):
        called.append(node)
    ingestor._embed_and_save = fake_embed_and_save
    await ingestor.ingest(mock_db_pool, batch_size=2)
    assert called
