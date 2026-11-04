"""
Workout Table Access Class

This object contains methods to access the workout table

Methods:
    get_all(user_id) - returns all workouts tied to the user_id 
    create(workout) - Adds workout to the table  
"""
from backend.db import (
    execute_select,
    get_db_connection
)


class WorkoutRepository:

    @staticmethod
    def get_all(user_id):
        return execute_select(
            """
            SELECT
                id,
                user_id,
                activity_type,
                duration_minutes,
                workout_date
            FROM workouts
            WHERE user_id = %s
            ORDER BY workout_date DESC, id DESC
            """,
            (user_id,)
        )

    @staticmethod
    def create(workout):
        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO workouts (
                    user_id,
                    activity_type,
                    duration_minutes,
                    workout_date
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    workout.user_id,
                    workout.activity_type,
                    workout.duration_minutes,
                    workout.workout_date
                )
            )

            workout_id = cursor.lastrowid
            connection.commit()
            return workout_id

        except Exception:
            if connection is not None:
                connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()

            if connection is not None:
                connection.close()
