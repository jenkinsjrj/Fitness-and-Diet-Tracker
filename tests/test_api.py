
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


def test_get_workouts():
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/api/workouts")

    assert response.status_code == 200

    workouts = response.get_json()

    assert isinstance(workouts, list)
    assert len(workouts) >= 3