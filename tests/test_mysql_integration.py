"""Optional real-MySQL integration test for Maxim's endpoints.

The ordinary test_api.py suite uses an in-memory fake database and should run
without Docker. To exercise actual SQL persistence, first start the project's
MySQL container and apply schema.sql, then run:

    RUN_MYSQL_INTEGRATION=1 python -m pytest -q tests/test_mysql_integration.py

PowerShell:
    $env:RUN_MYSQL_INTEGRATION = "1"
    python -m pytest -q tests/test_mysql_integration.py

This test creates and removes its own temporary user and related records.
"""

import os
import uuid
from datetime import date, timedelta

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MYSQL_INTEGRATION") != "1",
    reason="Set RUN_MYSQL_INTEGRATION=1 to run tests against the configured MySQL database",
)


def test_workout_weight_and_progress_persist_in_mysql():
    from backend.app import create_app
    from backend.db import get_db_connection

    connection = get_db_connection()
    cursor = connection.cursor()
    user_id = None
    try:
        cursor.execute(
            """
            INSERT INTO users
                (name, height_cm, goal_weight_kg, daily_calorie_target, weekly_workout_target)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (f"Maxim API Test {uuid.uuid4().hex[:8]}", 180.0, 80.0, 2000, 2),
        )
        user_id = cursor.lastrowid
        connection.commit()

        app = create_app({"TESTING": True, "DEFAULT_USER_ID": user_id})
        client = app.test_client()
        today = date.today()
        monday = today - timedelta(days=today.weekday())

        first_workout = client.post(
            "/api/workouts",
            json={
                "activity_type": "Integration Run",
                "duration_minutes": 30,
                "workout_date": monday.isoformat(),
            },
        )
        second_workout = client.post(
            "/api/workouts",
            json={
                "activity_type": "Integration Ride",
                "duration_minutes": 20,
                "workout_date": today.isoformat(),
            },
        )
        first_weight = client.post(
            "/api/weights",
            json={"weight_kg": 85.0, "recorded_date": monday.isoformat()},
        )
        second_weight = client.post(
            "/api/weights",
            json={"weight_kg": 84.0, "recorded_date": today.isoformat()},
        )

        assert first_workout.status_code == 201
        assert second_workout.status_code == 201
        assert first_weight.status_code == 201
        assert second_weight.status_code == 201

        workouts = client.get("/api/workouts")
        weights = client.get("/api/weights")
        progress = client.get(f"/api/progress?week_start={monday.isoformat()}")

        assert workouts.status_code == 200
        assert len(workouts.get_json()) == 2
        assert weights.status_code == 200
        assert len(weights.get_json()) == 2
        assert progress.status_code == 200
        summary = progress.get_json()
        assert summary["workouts"]["count"] == 2
        assert summary["workouts"]["total_minutes"] == 50
        assert summary["workouts"]["goal_met"] is True
        assert summary["weight"]["current_weight_kg"] == 84.0

        deleted_id = first_workout.get_json()["workout"]["id"]
        deleted = client.delete(f"/api/workouts/{deleted_id}")
        assert deleted.status_code == 200
        assert all(item["id"] != deleted_id for item in client.get("/api/workouts").get_json())

        invalid = client.post(
            "/api/workouts",
            json={
                "activity_type": "Invalid Test",
                "duration_minutes": -1,
                "workout_date": today.isoformat(),
            },
        )
        assert invalid.status_code == 400
    finally:
        if user_id is not None:
            cursor.execute("DELETE FROM workouts WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM weight_history WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
        cursor.close()
        connection.close()
