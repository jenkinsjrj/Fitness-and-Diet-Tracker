"""SQL access for the workouts table."""

from backend.db import execute_select, get_db_connection


class WorkoutRepository:
    """Read and write workout records in MySQL."""

    @staticmethod
    def get_all(user_id: int) -> list[dict]:
        return execute_select(
            """
            SELECT id, user_id, activity_type, duration_minutes, workout_date
            FROM workouts
            WHERE user_id = %s
            ORDER BY workout_date DESC, id DESC
            """,
            (user_id,),
        )

    @staticmethod
    def create(workout) -> int:
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO workouts (
                    user_id, activity_type, duration_minutes, workout_date
                ) VALUES (%s, %s, %s, %s)
                """,
                (
                    workout.user_id,
                    workout.activity_type,
                    workout.duration_minutes,
                    workout.workout_date,
                ),
            )
            workout_id = cursor.lastrowid
            connection.commit()
            return int(workout_id)
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
    def delete(user_id: int, workout_id: int) -> bool:
        """Delete only a workout owned by user_id; return whether one row changed."""
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM workouts WHERE id = %s AND user_id = %s",
                (workout_id, user_id),
            )
            deleted = cursor.rowcount > 0
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

    @staticmethod
    def get_weekly_summary(user_id: int, week_start, week_end) -> dict:
        """Return the count and total duration for an inclusive date range."""
        rows = execute_select(
            """
            SELECT
                COUNT(*) AS workout_count,
                COALESCE(SUM(duration_minutes), 0) AS total_minutes
            FROM workouts
            WHERE user_id = %s
              AND workout_date >= %s
              AND workout_date <= %s
            """,
            (user_id, week_start, week_end),
        )
        return rows[0] if rows else {"workout_count": 0, "total_minutes": 0}
