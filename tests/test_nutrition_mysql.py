"""Optional real-MySQL checks using temporary users and foods.

PowerShell, after starting the project's database:
    $env:RUN_MYSQL_INTEGRATION = "1"
    python -m pytest -q tests/test_nutrition_mysql.py
    Remove-Item Env:RUN_MYSQL_INTEGRATION
"""

import os
import uuid

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MYSQL_INTEGRATION") != "1",
    reason="Set RUN_MYSQL_INTEGRATION=1 to check the configured MySQL database",
)


def test_meals_persist_totals_recommendations_and_delete():
    from backend.app import create_app
    from backend.db import execute_select, get_db_connection

    connection = get_db_connection()
    cursor = connection.cursor()
    users = []
    foods = []
    suffix = uuid.uuid4().hex[:8]
    try:
        for label in ("A", "B"):
            cursor.execute(
                """INSERT INTO users (name, daily_calorie_target, weekly_workout_target)
                   VALUES (%s, %s, %s)""",
                (f"Trent test {label} {suffix}", 452, 3),
            )
            users.append(cursor.lastrowid)
        for name, values in (("Egg", (72, 6.3, 0.4, 4.8)), ("Oatmeal", (154, 6, 27, 3))):
            cursor.execute(
                """INSERT INTO foods
                   (name, serving_description, calories, protein_g, carbs_g, fat_g)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (f"Trent test {name} {suffix}", "1 test serving", *values),
            )
            foods.append(cursor.lastrowid)
        connection.commit()

        config = {"TESTING": True, "DEFAULT_USER_ID": users[0]}
        http = create_app(config).test_client()
        payload = {
            "meal_type": "Breakfast", "meal_date": "2026-11-03",
            "items": [{"food_id": foods[0], "servings": 2},
                      {"food_id": foods[1], "servings": 1}],
        }
        created = http.post("/api/meals", json=payload)
        assert created.status_code == 201
        meal_id = created.get_json()["meal"]["id"]

        # A fresh app instance reads the persisted records through new DB connections.
        restarted = create_app(config).test_client()
        listed = restarted.get("/api/meals?date=2026-11-03")
        assert listed.status_code == 200
        assert listed.get_json()[0]["id"] == meal_id
        assert len(listed.get_json()[0]["items"]) == 2
        result = restarted.get("/api/nutrition?date=2026-11-03").get_json()
        assert result["calories"] == 298
        assert result["protein_g"] == 18.6
        assert result["carbs_g"] == 27.8
        assert result["fat_g"] == 12.6
        suggestions = restarted.get("/api/recommendations?date=2026-11-03").get_json()
        assert suggestions["remaining_calories"] == 154
        assert set(foods).issubset({food["id"] for food in suggestions["foods"]})
        assert all(food["calories"] <= 154 for food in suggestions["foods"])

        other = create_app({"TESTING": True, "DEFAULT_USER_ID": users[1]}).test_client()
        assert other.get("/api/meals?date=2026-11-03").get_json() == []
        assert other.delete(f"/api/meals/{meal_id}").status_code == 404
        assert restarted.get("/api/nutrition?date=2026-11-04").get_json()["calories"] == 0

        payload["items"][0]["servings"] = -1
        assert http.post("/api/meals", json=payload).status_code == 400
        assert len(restarted.get("/api/meals?date=2026-11-03").get_json()) == 1

        assert restarted.delete(f"/api/meals/{meal_id}").status_code == 200
        assert restarted.get("/api/nutrition?date=2026-11-03").get_json()["calories"] == 0
        assert execute_select("SELECT id FROM meal_items WHERE meal_id = %s", (meal_id,)) == []
    finally:
        # Remove only records created by this test. Preserve the demo user's data.
        for user_id in users:
            cursor.execute("DELETE FROM meals WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        for food_id in foods:
            cursor.execute("DELETE FROM foods WHERE id = %s", (food_id,))
        connection.commit()
        cursor.close()
        connection.close()
