from src.agentic.api.v1.general import root, health

def test_root():
    resp = root()
    assert "message" in resp

def test_health():
    resp = health()
    assert resp["status"] == "ok"
