"""SQL queries needed by progress tracking."""

from backend.db import execute_select


class ProgressRepository:
    """Read the user's fitness targets from the users table."""

    @staticmethod
    def get_user_targets(user_id: int) -> dict | None:
        rows = execute_select(
            """
            SELECT weekly_workout_target, goal_weight_kg
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        return rows[0] if rows else None
