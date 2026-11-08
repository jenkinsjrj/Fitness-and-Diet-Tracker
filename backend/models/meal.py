"""Meal data and validation for Trent's nutrition tracker."""

from datetime import date
from decimal import Decimal


class MealItem:
    """One food and the number of servings eaten."""

    def __init__(self, food_id, servings):
        if type(food_id) is not int or not 1 <= food_id <= 2147483647:
            raise ValueError("food_id must be a positive integer")
        if type(servings) not in (int, float, Decimal):
            raise ValueError("servings must be a number")

        amount = Decimal(str(servings))
        if not amount.is_finite() or not 0 < amount <= Decimal("9999.99"):
            raise ValueError("servings must be greater than 0 and at most 9999.99")
        if amount != amount.quantize(Decimal("0.01")):
            raise ValueError("servings may have at most two decimal places")

        self.food_id = food_id
        self.servings = amount


class Meal:
    """A dated meal containing one or more MealItem objects."""

    def __init__(self, user_id, meal_type, meal_date, items):
        if type(user_id) is not int or user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        if not isinstance(meal_type, str):
            raise ValueError("meal_type is required")
        meal_type = meal_type.strip().capitalize()
        if meal_type not in ("Breakfast", "Lunch", "Dinner", "Snack"):
            raise ValueError("meal_type must be Breakfast, Lunch, Dinner, or Snack")
        if type(meal_date) is not date or meal_date.year < 1000:
            raise ValueError("meal_date must be a valid MySQL date (year 1000 or later)")
        if not isinstance(items, list) or not items:
            raise ValueError("items must be a nonempty list")
        if any(not isinstance(item, MealItem) for item in items):
            raise ValueError("Each item must contain a food_id and servings")

        self.user_id = user_id
        self.meal_type = meal_type
        self.meal_date = meal_date
        self.items = items
