"""Flask endpoints for nutrition tracking and food recommendations."""

from datetime import date

import mysql.connector
from flask import Blueprint, current_app, jsonify, request

from backend.models.meal import Meal, MealItem
from backend.routes.validators import parse_iso_date
from backend.services.nutrition_service import NutritionService
from backend.services.recommendation_service import RecommendationService


nutrition_bp = Blueprint("nutrition", __name__, url_prefix="/api")


def _user_id():
    # Use the same predefined demo user as the existing workout routes.
    return int(current_app.config["DEFAULT_USER_ID"])


def _selected_date():
    selected = parse_iso_date(request.args.get("date", date.today().isoformat()), "date")
    if selected.year < 1000:
        raise ValueError("date must have a year of 1000 or later")
    return selected


@nutrition_bp.errorhandler(ValueError)
def invalid_input(error):
    return jsonify({"error": str(error)}), 400


@nutrition_bp.errorhandler(LookupError)
def missing_user(error):
    return jsonify({"error": str(error)}), 404


@nutrition_bp.errorhandler(mysql.connector.Error)
def database_error(error):
    current_app.logger.exception("Database error in nutrition feature")
    return jsonify({"error": "Unable to complete the nutrition database request"}), 500


@nutrition_bp.get("/foods")
def get_foods():
    return jsonify(NutritionService.get_foods()), 200


@nutrition_bp.post("/meals")
def create_meal():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("A JSON object is required")
    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("items must be a nonempty list")

    items = []
    for item in raw_items:
        if not isinstance(item, dict):
            raise ValueError("Each item must contain a food_id and servings")
        items.append(MealItem(item.get("food_id"), item.get("servings")))

    meal = Meal(
        user_id=_user_id(),
        meal_type=data.get("meal_type"),
        meal_date=parse_iso_date(data.get("meal_date"), "meal_date"),
        items=items,
    )
    meal_id = NutritionService.add_meal(meal)
    return jsonify({
        "message": "Meal created",
        "meal": {
            "id": meal_id,
            "user_id": meal.user_id,
            "meal_type": meal.meal_type,
            "meal_date": meal.meal_date.isoformat(),
            "items": [
                {"food_id": item.food_id, "servings": float(item.servings)}
                for item in meal.items
            ],
        },
    }), 201


@nutrition_bp.get("/meals")
def get_meals():
    return jsonify(NutritionService.get_meals(_user_id(), _selected_date())), 200


@nutrition_bp.get("/nutrition")
def get_nutrition():
    return jsonify(NutritionService.get_daily_summary(_user_id(), _selected_date())), 200


@nutrition_bp.get("/recommendations")
def get_recommendations():
    return jsonify(RecommendationService.recommend_foods(_user_id(), _selected_date())), 200


@nutrition_bp.delete("/meals/<int:meal_id>")
def delete_meal(meal_id):
    if not NutritionService.delete_meal(_user_id(), meal_id):
        return jsonify({"error": "Meal was not found"}), 404
    return jsonify({"message": "Meal deleted", "id": meal_id}), 200
