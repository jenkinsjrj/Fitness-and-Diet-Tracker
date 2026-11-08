"""Meal logging and daily nutrition calculations."""

from decimal import Decimal

from backend.repositories.nutrition_repository import NutritionRepository


NUTRIENTS = ("calories", "protein_g", "carbs_g", "fat_g")


class NutritionService:
    @staticmethod
    def get_foods():
        foods = NutritionRepository.get_foods()
        result = []
        for food in foods:
            record = dict(food)
            for nutrient in NUTRIENTS:
                record[nutrient] = float(food[nutrient])
            result.append(record)
        return result

    @staticmethod
    def get_calorie_target(user_id):
        target = NutritionRepository.get_calorie_target(user_id)
        if target is None:
            raise LookupError("User was not found")
        return target

    @staticmethod
    def add_meal(meal):
        NutritionService.get_calorie_target(meal.user_id)
        food_ids = {food["id"] for food in NutritionRepository.get_foods()}
        for item in meal.items:
            if item.food_id not in food_ids:
                raise ValueError(f"Food {item.food_id} was not found")
        return NutritionRepository.create(meal)

    @staticmethod
    def get_meals(user_id, meal_date):
        NutritionService.get_calorie_target(user_id)
        meals = {}
        for row in NutritionRepository.get_meal_rows(user_id, meal_date):
            meal_id = row["meal_id"]
            if meal_id not in meals:
                meals[meal_id] = {
                    "id": meal_id,
                    "meal_type": row["meal_type"],
                    "meal_date": row["meal_date"].isoformat(),
                    "items": [],
                }
            if row["food_id"] is not None:
                item = {
                    "food_id": row["food_id"],
                    "name": row["name"],
                    "serving_description": row["serving_description"],
                    "servings": float(row["servings"]),
                }
                for nutrient in NUTRIENTS:
                    item[nutrient] = float(
                        Decimal(str(row[nutrient])) * Decimal(str(row["servings"]))
                    )
                meals[meal_id]["items"].append(item)
        return list(meals.values())

    @staticmethod
    def get_daily_summary(user_id, meal_date):
        target = NutritionService.get_calorie_target(user_id)
        totals = {nutrient: Decimal("0") for nutrient in NUTRIENTS}
        for row in NutritionRepository.get_meal_rows(user_id, meal_date):
            if row["food_id"] is not None:
                for nutrient in NUTRIENTS:
                    totals[nutrient] += (
                        Decimal(str(row[nutrient])) * Decimal(str(row["servings"]))
                    )

        summary = {
            "user_id": user_id,
            "date": meal_date.isoformat(),
            "daily_calorie_target": int(target),
            "remaining_calories": float(Decimal(str(target)) - totals["calories"]),
        }
        for nutrient in NUTRIENTS:
            summary[nutrient] = float(totals[nutrient])
        return summary

    @staticmethod
    def delete_meal(user_id, meal_id):
        NutritionService.get_calorie_target(user_id)
        return NutritionRepository.delete(user_id, meal_id)
