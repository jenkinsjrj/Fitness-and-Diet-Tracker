
from backend.app import app


def test_health_endpoint():
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_home_endpoint():
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["status"] == "running"