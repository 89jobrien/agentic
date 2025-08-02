def test_root():
    from agentic.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Agentic" in resp.json()["message"]
