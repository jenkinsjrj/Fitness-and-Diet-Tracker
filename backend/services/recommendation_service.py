"""Simple food suggestions based on the remaining daily calorie allowance."""

from decimal import Decimal

from backend.services.nutrition_service import NutritionService


class RecommendationService:
    @staticmethod
    def recommend_foods(user_id, meal_date):
        summary = NutritionService.get_daily_summary(user_id, meal_date)
        remaining = Decimal(str(summary["remaining_calories"]))
        suggestions = []

        if remaining > 0:
            for food in NutritionService.get_foods():
                if Decimal(str(food["calories"])) <= remaining:
                    suggestions.append(food)
            # Deterministic ordering makes results easy to explain and test.
            suggestions.sort(key=lambda food: (food["calories"], food["name"], food["id"]))

        if remaining <= 0:
            message = "The daily calorie target has been reached or exceeded."
        elif not suggestions:
            message = "No foods in the database fit the remaining calories."
        else:
            message = "Each suggestion is one serving; choose individually, not all together."

        return {
            "user_id": user_id,
            "date": meal_date.isoformat(),
            "daily_calorie_target": summary["daily_calorie_target"],
            "calories_eaten": summary["calories"],
            "remaining_calories": summary["remaining_calories"],
            "message": message,
            "foods": suggestions,
        }
