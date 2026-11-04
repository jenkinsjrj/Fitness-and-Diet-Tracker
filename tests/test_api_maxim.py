"""API and business-logic tests for Maxim's workout/progress features.

These tests use an in-memory fake store. They exercise Flask routes, input
validation, service calculations, and response formats without requiring MySQL.
Run from the repository root with: python -m pytest -q
"""

from datetime import date
from decimal import Decimal

import pytest

from backend.app import create_app
from backend.repositories.progress_repository import ProgressRepository
from backend.repositories.weight_repository import WeightRepository
from backend.repositories.workout_repository import WorkoutRepository


class FakeStore:
    """A small in-memory stand-in for the MySQL repository methods."""

    def __init__(self):
        self.workouts = []
        self.weights = []
        self.next_workout_id = 1
        self.next_weight_id = 1
        self.targets = {
            "weekly_workout_target": 3,
            "goal_weight_kg": Decimal("80.00"),
        }

    def get_workouts(self, user_id):
        records = [w.copy() for w in self.workouts if w["user_id"] == user_id]
        return sorted(
            records,
            key=lambda w: (w["workout_date"], w["id"]),
            reverse=True,
        )

    def add_workout(self, workout):
        workout_id = self.next_workout_id
        self.next_workout_id += 1
        self.workouts.append(
            {
                "id": workout_id,
                "user_id": workout.user_id,
                "activity_type": workout.activity_type,
                "duration_minutes": workout.duration_minutes,
                "workout_date": workout.workout_date,
            }
        )
        return workout_id

    def delete_workout(self, user_id, workout_id):
        for index, workout in enumerate(self.workouts):
            if workout["user_id"] == user_id and workout["id"] == workout_id:
                del self.workouts[index]
                return True
        return False

    def get_weekly_summary(self, user_id, week_start, week_end):
        matching = [
            w
            for w in self.workouts
            if w["user_id"] == user_id
            and week_start <= w["workout_date"] <= week_end
        ]
        return {
            "workout_count": len(matching),
            "total_minutes": sum(w["duration_minutes"] for w in matching),
        }

    def get_weights(self, user_id):
        records = [w.copy() for w in self.weights if w["user_id"] == user_id]
        return sorted(records, key=lambda w: (w["recorded_date"], w["id"]))

    def add_weight(self, entry):
        weight_id = self.next_weight_id
        self.next_weight_id += 1
        self.weights.append(
            {
                "id": weight_id,
                "user_id": entry.user_id,
                "weight_kg": entry.weight_kg,
                "recorded_date": entry.recorded_date,
            }
        )
        return weight_id

    def get_targets(self, user_id):
        return self.targets.copy() if user_id == 1 else None


@pytest.fixture

def client(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr(WorkoutRepository, "get_all", staticmethod(store.get_workouts))
    monkeypatch.setattr(WorkoutRepository, "create", staticmethod(store.add_workout))
    monkeypatch.setattr(WorkoutRepository, "delete", staticmethod(store.delete_workout))
    monkeypatch.setattr(
        WorkoutRepository,
        "get_weekly_summary",
        staticmethod(store.get_weekly_summary),
    )
    monkeypatch.setattr(WeightRepository, "get_all", staticmethod(store.get_weights))
    monkeypatch.setattr(WeightRepository, "create", staticmethod(store.add_weight))
    monkeypatch.setattr(
        ProgressRepository, "get_user_targets", staticmethod(store.get_targets)
    )

    app = create_app({"TESTING": True, "DEFAULT_USER_ID": 1})
    return app.test_client(), store


def test_home_and_health_endpoints(client):
    http, _ = client

    home = http.get("/")
    health = http.get("/api/health")

    assert home.status_code == 200
    assert home.get_json()["status"] == "running"
    assert health.status_code == 200
    assert health.get_json() == {"status": "healthy"}


def test_create_and_list_workout(client):
    http, _ = client

    created = http.post(
        "/api/workouts",
        json={
            "activity_type": "  Running  ",
            "duration_minutes": 30,
            "workout_date": "2026-11-02",
        },
    )
    listed = http.get("/api/workouts")

    assert created.status_code == 201
    body = created.get_json()["workout"]
    assert body == {
        "id": 1,
        "user_id": 1,
        "activity_type": "Running",
        "duration_minutes": 30,
        "workout_date": "2026-11-02",
    }
    assert listed.status_code == 200
    assert listed.get_json()[0]["activity_type"] == "Running"
    assert listed.get_json()[0]["workout_date"] == "2026-11-02"


@pytest.mark.parametrize(
    "payload",
    [
        {"activity_type": "Run", "duration_minutes": 0, "workout_date": "2026-11-02"},
        {"activity_type": "Run", "duration_minutes": -5, "workout_date": "2026-11-02"},
        {"activity_type": "Run", "duration_minutes": 30.5, "workout_date": "2026-11-02"},
        {"activity_type": "Run", "duration_minutes": True, "workout_date": "2026-11-02"},
        {"activity_type": "   ", "duration_minutes": 30, "workout_date": "2026-11-02"},
        {"activity_type": "R" * 101, "duration_minutes": 30, "workout_date": "2026-11-02"},
        {"activity_type": "Run", "duration_minutes": 30, "workout_date": "11/02/2026"},
        {"activity_type": "Run", "duration_minutes": 30, "workout_date": "2026-02-30"},
    ],
)
def test_invalid_workout_data_is_rejected(client, payload):
    http, store = client

    response = http.post("/api/workouts", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()
    assert store.workouts == []


def test_missing_or_non_json_workout_body_is_rejected(client):
    http, store = client

    response = http.post("/api/workouts", data="not-json", content_type="text/plain")

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"
    assert store.workouts == []


def test_delete_workout_and_not_found_case(client):
    http, _ = client
    created = http.post(
        "/api/workouts",
        json={
            "activity_type": "Cycling",
            "duration_minutes": 45,
            "workout_date": "2026-11-03",
        },
    )
    workout_id = created.get_json()["workout"]["id"]

    deleted = http.delete(f"/api/workouts/{workout_id}")
    missing = http.delete(f"/api/workouts/{workout_id}")

    assert deleted.status_code == 200
    assert deleted.get_json()["id"] == workout_id
    assert missing.status_code == 404


def test_create_and_retrieve_weight_entries(client):
    http, _ = client

    created = http.post(
        "/api/weights",
        json={"weight_kg": 84.5, "recorded_date": "2026-11-02"},
    )
    listed = http.get("/api/weights")

    assert created.status_code == 201
    assert created.get_json()["weight"] == {
        "id": 1,
        "user_id": 1,
        "weight_kg": 84.5,
        "recorded_date": "2026-11-02",
    }
    assert listed.status_code == 200
    assert listed.get_json()[0]["weight_kg"] == 84.5


@pytest.mark.parametrize(
    "weight",
    [None, 0, -1, True, "84.5", 1000, 84.567, float("inf"), float("nan")],
)
def test_invalid_weight_values_are_rejected(client, weight):
    http, store = client

    response = http.post(
        "/api/weights",
        json={"weight_kg": weight, "recorded_date": "2026-11-02"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
    assert store.weights == []


def test_invalid_weight_date_is_rejected(client):
    http, store = client

    response = http.post(
        "/api/weights",
        json={"weight_kg": 80, "recorded_date": "2026-13-01"},
    )

    assert response.status_code == 400
    assert store.weights == []


def test_progress_summarizes_weekly_workouts_and_weight_change(client):
    http, _ = client

    # Week of 2026-11-02 (Monday through Sunday); the prior Sunday's workout
    # must not be included in this week's totals.
    http.post(
        "/api/workouts",
        json={"activity_type": "Run", "duration_minutes": 30, "workout_date": "2026-11-01"},
    )
    http.post(
        "/api/workouts",
        json={"activity_type": "Run", "duration_minutes": 30, "workout_date": "2026-11-02"},
    )
    http.post(
        "/api/workouts",
        json={"activity_type": "Cycling", "duration_minutes": 45, "workout_date": "2026-11-03"},
    )
    http.post(
        "/api/weights",
        json={"weight_kg": 85.0, "recorded_date": "2026-10-27"},
    )
    http.post(
        "/api/weights",
        json={"weight_kg": 84.0, "recorded_date": "2026-11-03"},
    )

    response = http.get("/api/progress?week_start=2026-11-02")
    result = response.get_json()

    assert response.status_code == 200
    assert result["week"] == {
        "start_date": "2026-11-02",
        "end_date": "2026-11-08",
    }
    assert result["workouts"] == {
        "count": 2,
        "total_minutes": 75,
        "weekly_goal": 3,
        "remaining": 1,
        "goal_progress_percentage": 66.7,
        "goal_met": False,
    }
    assert result["weight"]["starting_weight_kg"] == 85.0
    assert result["weight"]["current_weight_kg"] == 84.0
    assert result["weight"]["change_since_first_record_kg"] == -1.0
    assert result["weight"]["goal_weight_kg"] == 80.0
    assert result["weight"]["goal_progress_percentage"] == 20.0
    assert result["weight"]["record_count"] == 2


def test_progress_rejects_week_start_that_is_not_monday(client):
    http, _ = client

    response = http.get("/api/progress?week_start=2026-11-03")

    assert response.status_code == 400
    assert "Monday" in response.get_json()["error"]


def test_progress_unknown_user_returns_not_found(client):
    http, _ = client
    # Configure a user ID that is not in the fake store.
    other_app = create_app({"TESTING": True, "DEFAULT_USER_ID": 999})
    response = other_app.test_client().get("/api/progress?week_start=2026-11-02")

    assert response.status_code == 404
    assert response.get_json()["error"] == "User was not found"


def test_progress_without_weight_history_returns_null_weight_metrics(client):
    http, _ = client

    response = http.get("/api/progress?week_start=2026-11-02")
    weight = response.get_json()["weight"]

    assert response.status_code == 200
    assert weight["record_count"] == 0
    assert weight["history"] == []
    assert weight["starting_weight_kg"] is None
    assert weight["current_weight_kg"] is None
    assert weight["change_since_first_record_kg"] is None
    assert weight["goal_progress_percentage"] is None
