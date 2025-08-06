from src.agentic.config import AppConfig, get_config

def test_config_structure(patch_config):
    cfg = get_config()
    assert isinstance(cfg, AppConfig)
    assert hasattr(cfg, "db")
    assert hasattr(cfg, "llm")
    assert hasattr(cfg, "rag")
