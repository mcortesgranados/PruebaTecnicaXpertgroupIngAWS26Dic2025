from fastapi.testclient import TestClient

from backend.app import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert "dataset" in response.json()
