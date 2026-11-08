"""SQL access for the existing foods, meals, and meal_items tables."""

from backend.db import execute_select, get_db_connection


class NutritionRepository:
    @staticmethod
    def get_foods():
        return execute_select(
            """
            SELECT id, name, serving_description, calories, protein_g, carbs_g, fat_g
            FROM foods
            ORDER BY name, id
            """
        )

    @staticmethod
    def get_calorie_target(user_id):
        rows = execute_select(
            "SELECT daily_calorie_target FROM users WHERE id = %s", (user_id,)
        )
        return rows[0]["daily_calorie_target"] if rows else None

    @staticmethod
    def create(meal):
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO meals (user_id, meal_type, meal_date)
                VALUES (%s, %s, %s)
                """,
                (meal.user_id, meal.meal_type, meal.meal_date),
            )
            meal_id = int(cursor.lastrowid)
            for item in meal.items:
                cursor.execute(
                    """
                    INSERT INTO meal_items (meal_id, food_id, servings)
                    VALUES (%s, %s, %s)
                    """,
                    (meal_id, item.food_id, item.servings),
                )
            # Save the meal and every item as one transaction.
            connection.commit()
            return meal_id
        except Exception:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    @staticmethod
    def get_meal_rows(user_id, meal_date):
        return execute_select(
            """
            SELECT m.id AS meal_id, m.meal_type, m.meal_date,
                   mi.id AS item_id, mi.food_id, mi.servings,
                   f.name, f.serving_description,
                   f.calories, f.protein_g, f.carbs_g, f.fat_g
            FROM meals m
            LEFT JOIN meal_items mi ON mi.meal_id = m.id
            LEFT JOIN foods f ON f.id = mi.food_id
            WHERE m.user_id = %s AND m.meal_date = %s
            ORDER BY m.id, mi.id
            """,
            (user_id, meal_date),
        )

    @staticmethod
    def delete(user_id, meal_id):
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM meals WHERE user_id = %s AND id = %s",
                (user_id, meal_id),
            )
            deleted = cursor.rowcount > 0
            # The schema's ON DELETE CASCADE removes the meal_items too.
            connection.commit()
            return deleted
        except Exception:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
