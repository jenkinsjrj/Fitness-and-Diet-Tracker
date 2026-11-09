
import pytest

from backend.app import create_app
from backend.repositories.reminder_repository import (
    ReminderRepository
)


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def reminder(client):
    response = client.post(
        "/api/reminders",
        json={
            "title": "Test Workout",
            "description": "30 minute run",
            "scheduled_at": "2026-11-12T17:00:00Z"
        }
    )

    assert response.status_code == 201

    created = response.get_json()
    reminder_id = created["id"]

    yield created

    # Remove the test record, even if a test fails.
    ReminderRepository.delete(reminder_id, 1)


def test_create_reminder(reminder):
    assert reminder["title"] == "Test Workout"
    assert reminder["completed"] is False
    assert reminder["scheduled_at"] == (
        "2026-11-12T17:00:00Z"
    )


def test_get_reminder(client, reminder):
    response = client.get(
        f"/api/reminders/{reminder['id']}"
    )

    assert response.status_code == 200
    assert response.get_json()["id"] == reminder["id"]


def test_calendar_date_filter(client, reminder):
    response = client.get(
        "/api/reminders?date=2026-11-12"
    )

    assert response.status_code == 200

    reminders = response.get_json()

    assert any(
        item["id"] == reminder["id"]
        for item in reminders
    )


def test_update_reminder(client, reminder):
    response = client.patch(
        f"/api/reminders/{reminder['id']}",
        json={"title": "Updated Workout"}
    )

    assert response.status_code == 200
    assert response.get_json()["title"] == (
        "Updated Workout"
    )


def test_mark_completed(client, reminder):
    response = client.patch(
        f"/api/reminders/{reminder['id']}",
        json={"completed": True}
    )

    assert response.status_code == 200
    assert response.get_json()["completed"] is True


def test_delete_reminder(client, reminder):
    response = client.delete(
        f"/api/reminders/{reminder['id']}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/reminders/{reminder['id']}"
    )

    assert response.status_code == 404


def test_invalid_title(client):
    response = client.post(
        "/api/reminders",
        json={
            "title": "",
            "scheduled_at": "2026-11-12T17:00:00Z"
        }
    )

    assert response.status_code == 400


def test_invalid_date(client):
    response = client.post(
        "/api/reminders",
        json={
            "title": "Workout",
            "scheduled_at": "not-a-date"
        }
    )

    assert response.status_code == 400


def test_invalid_completion_type(client, reminder):
    response = client.patch(
        f"/api/reminders/{reminder['id']}",
        json={"completed": "yes"}
    )

    assert response.status_code == 400


def test_missing_reminder(client):
    response = client.get(
        "/api/reminders/999999999"
    )

    assert response.status_code == 404


def test_invalid_calendar_date(client):
    response = client.get(
        "/api/reminders?date=not-a-date"
    )

    assert response.status_code == 400
