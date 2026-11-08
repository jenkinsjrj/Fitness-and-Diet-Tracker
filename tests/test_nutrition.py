"""Trent's API/calculation tests. No running MySQL server is needed.

Run: python -m pytest -q tests/test_nutrition.py
Only the database repository is replaced; real routes and services are tested.
"""

from copy import deepcopy
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import mysql.connector
import pytest

from backend.app import create_app
from backend.models.meal import Meal, MealItem
from backend.repositories.nutrition_repository import NutritionRepository


class FakeStore:
    def __init__(self):
        self.targets = {1: 2500, 2: 2000}
        self.foods = [
            {"id": 1, "name": "Egg", "serving_description": "1 large egg",
             "calories": Decimal("72"), "protein_g": Decimal("6.3"),
             "carbs_g": Decimal("0.4"), "fat_g": Decimal("4.8")},
            {"id": 2, "name": "Oatmeal", "serving_description": "1 cup cooked",
             "calories": Decimal("154"), "protein_g": Decimal("6"),
             "carbs_g": Decimal("27"), "fat_g": Decimal("3")},
            {"id": 3, "name": "Chicken Breast", "serving_description": "100 g cooked",
             "calories": Decimal("165"), "protein_g": Decimal("31"),
             "carbs_g": Decimal("0"), "fat_g": Decimal("3.6")},
        ]
        self.meals = {}
        self.next_id = 1

    def get_foods(self):
        return deepcopy(self.foods)

    def get_target(self, user_id):
        return self.targets.get(user_id)

    def create(self, meal):
        meal_id = self.next_id
        self.next_id += 1
        self.meals[meal_id] = meal
        return meal_id

    def get_rows(self, user_id, meal_date):
        rows = []
        for meal_id, meal in self.meals.items():
            if meal.user_id != user_id or meal.meal_date != meal_date:
                continue
            for index, item in enumerate(meal.items):
                food = next(food for food in self.foods if food["id"] == item.food_id)
                rows.append({
                    **food, "meal_id": meal_id, "meal_type": meal.meal_type,
                    "meal_date": meal.meal_date, "item_id": index + 1,
                    "food_id": item.food_id, "servings": item.servings,
                })
        return rows

    def delete(self, user_id, meal_id):
        meal = self.meals.get(meal_id)
        if meal is None or meal.user_id != user_id:
            return False
        del self.meals[meal_id]
        return True


@pytest.fixture
def client(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr(NutritionRepository, "get_foods", staticmethod(store.get_foods))
    monkeypatch.setattr(NutritionRepository, "get_calorie_target", staticmethod(store.get_target))
    monkeypatch.setattr(NutritionRepository, "create", staticmethod(store.create))
    monkeypatch.setattr(NutritionRepository, "get_meal_rows", staticmethod(store.get_rows))
    monkeypatch.setattr(NutritionRepository, "delete", staticmethod(store.delete))
    app = create_app({"TESTING": True, "DEFAULT_USER_ID": 1})
    return app.test_client(), store


def breakfast():
    return {
        "meal_type": "Breakfast", "meal_date": "2026-11-03",
        "items": [{"food_id": 1, "servings": 2}, {"food_id": 2, "servings": 1}],
    }


def test_food_list_uses_json_numbers(client):
    http, _ = client
    response = http.get("/api/foods")
    assert response.status_code == 200
    assert response.get_json()[0]["calories"] == 72.0
    assert response.get_json()[0]["serving_description"] == "1 large egg"


def test_log_list_and_calculate_sample_breakfast(client):
    http, _ = client
    created = http.post("/api/meals", json=breakfast())
    assert created.status_code == 201
    assert created.get_json()["meal"]["id"] == 1

    meals = http.get("/api/meals?date=2026-11-03")
    assert meals.status_code == 200
    assert len(meals.get_json()) == 1
    assert meals.get_json()[0]["meal_date"] == "2026-11-03"
    assert meals.get_json()[0]["items"][0]["calories"] == 144

    totals = http.get("/api/nutrition?date=2026-11-03")
    assert totals.status_code == 200
    assert totals.get_json() == {
        "user_id": 1, "date": "2026-11-03", "daily_calorie_target": 2500,
        "remaining_calories": 2202, "calories": 298,
        "protein_g": 18.6, "carbs_g": 27.8, "fat_g": 12.6,
    }


def test_multiple_meals_and_fractional_servings(client):
    http, _ = client
    http.post("/api/meals", json=breakfast())
    http.post("/api/meals", json={
        "meal_type": "  snack  ", "meal_date": "2026-11-03",
        "items": [{"food_id": 1, "servings": 0.5}],
    })
    summary = http.get("/api/nutrition?date=2026-11-03").get_json()
    assert summary["calories"] == 334
    assert summary["protein_g"] == 21.75
    assert http.get("/api/meals?date=2026-11-03").get_json()[1]["meal_type"] == "Snack"


def test_empty_day_and_default_date(client):
    http, _ = client
    summary = http.get("/api/nutrition?date=2026-11-04").get_json()
    assert summary["calories"] == 0
    assert summary["remaining_calories"] == 2500
    assert http.get("/api/meals?date=2026-11-04").get_json() == []
    assert http.get("/api/nutrition").get_json()["date"] == date.today().isoformat()


def test_dates_and_users_are_separate(client):
    http, store = client
    http.post("/api/meals", json=breakfast())
    other = create_app({"TESTING": True, "DEFAULT_USER_ID": 2}).test_client()
    assert other.get("/api/meals?date=2026-11-03").get_json() == []
    assert other.get("/api/nutrition?date=2026-11-03").get_json()["calories"] == 0
    assert other.delete("/api/meals/1").status_code == 404
    assert len(store.meals) == 1
    assert http.get("/api/nutrition?date=2026-11-04").get_json()["calories"] == 0


def test_caller_cannot_override_demo_user(client):
    http, store = client
    payload = breakfast()
    payload["user_id"] = 2
    http.post("/api/meals", json=payload)
    assert store.meals[1].user_id == 1


def test_delete_meal_updates_totals(client):
    http, _ = client
    http.post("/api/meals", json=breakfast())
    assert http.delete("/api/meals/1").status_code == 200
    assert http.get("/api/nutrition?date=2026-11-03").get_json()["calories"] == 0
    assert http.delete("/api/meals/1").status_code == 404


@pytest.mark.parametrize("servings", [None, 0, -1, True, "2", 0.001, 10000, float("inf"), float("nan")])
def test_invalid_servings_are_rejected_before_saving(client, servings):
    http, store = client
    payload = breakfast()
    payload["items"][0]["servings"] = servings
    response = http.post("/api/meals", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert store.meals == {}


@pytest.mark.parametrize("food_id", [None, 0, -1, True, "1", 1.5, 2147483648, 999])
def test_invalid_or_unknown_food_is_rejected(client, food_id):
    http, store = client
    payload = breakfast()
    payload["items"][1]["food_id"] = food_id
    assert http.post("/api/meals", json=payload).status_code == 400
    assert store.meals == {}


@pytest.mark.parametrize("field,value", [
    ("meal_date", "2026-02-30"), ("meal_date", "11/03/2026"),
    ("meal_date", "20261103"), ("meal_date", None), ("meal_date", "0999-01-01"),
    ("meal_type", ""), ("meal_type", "Dessert"), ("meal_type", None),
    ("items", []), ("items", {}), ("items", [None]), ("items", [{}]),
])
def test_invalid_meal_fields(client, field, value):
    http, store = client
    payload = breakfast()
    payload[field] = value
    assert http.post("/api/meals", json=payload).status_code == 400
    assert store.meals == {}


@pytest.mark.parametrize("payload", [[], None, "text"])
def test_non_object_json(client, payload):
    http, _ = client
    assert http.post("/api/meals", json=payload).status_code == 400


def test_malformed_json(client):
    http, _ = client
    response = http.post("/api/meals", data="{", content_type="application/json")
    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


@pytest.mark.parametrize("endpoint", ["meals", "nutrition", "recommendations"])
def test_invalid_query_date(client, endpoint):
    http, _ = client
    assert http.get(f"/api/{endpoint}?date=bad").status_code == 400


@pytest.mark.parametrize("endpoint", ["meals", "nutrition", "recommendations"])
def test_unknown_user(client, endpoint):
    other = create_app({"TESTING": True, "DEFAULT_USER_ID": 999}).test_client()
    assert other.get(f"/api/{endpoint}?date=2026-11-03").status_code == 404


def test_recommendations_respect_budget_including_exact_fit(client):
    http, store = client
    store.targets[1] = 452  # 452 - 298 = 154 calories remaining.
    http.post("/api/meals", json=breakfast())
    response = http.get("/api/recommendations?date=2026-11-03")
    assert response.status_code == 200
    result = response.get_json()
    assert result["remaining_calories"] == 154
    assert [food["name"] for food in result["foods"]] == ["Egg", "Oatmeal"]


@pytest.mark.parametrize("target,remaining", [(298, 0), (250, -48), (300, 2)])
def test_recommendations_when_no_food_fits(client, target, remaining):
    http, store = client
    store.targets[1] = target
    http.post("/api/meals", json=breakfast())
    result = http.get("/api/recommendations?date=2026-11-03").get_json()
    assert result["remaining_calories"] == remaining
    assert result["foods"] == []
    assert result["message"]


def test_empty_food_catalog(client):
    http, store = client
    store.foods = []
    assert http.get("/api/foods").get_json() == []
    assert http.get("/api/recommendations?date=2026-11-03").get_json()["foods"] == []


def test_database_errors_return_json_without_database_details(client, monkeypatch):
    http, _ = client
    def fail():
        raise mysql.connector.Error("private connection detail")
    monkeypatch.setattr(NutritionRepository, "get_foods", staticmethod(fail))
    response = http.get("/api/foods")
    assert response.status_code == 500
    assert "private connection detail" not in response.get_data(as_text=True)


def test_failed_item_insert_rolls_back_entire_transaction(monkeypatch):
    connection = MagicMock()
    cursor = connection.cursor.return_value
    cursor.lastrowid = 7
    cursor.execute.side_effect = [None, None, mysql.connector.Error("insert failed")]
    monkeypatch.setattr(
        "backend.repositories.nutrition_repository.get_db_connection", lambda: connection
    )
    meal = Meal(1, "Breakfast", date(2026, 11, 3), [MealItem(1, 2), MealItem(2, 1)])
    with pytest.raises(mysql.connector.Error):
        NutritionRepository.create(meal)
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
