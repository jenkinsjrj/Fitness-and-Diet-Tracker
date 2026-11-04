"""SQL access for the weight_history table."""

from backend.db import execute_select, get_db_connection


class WeightRepository:
    """Read and write body-weight history in MySQL."""

    @staticmethod
    def get_all(user_id: int) -> list[dict]:
        return execute_select(
            """
            SELECT id, user_id, weight_kg, recorded_date
            FROM weight_history
            WHERE user_id = %s
            ORDER BY recorded_date ASC, id ASC
            """,
            (user_id,),
        )

    @staticmethod
    def create(weight_entry) -> int:
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO weight_history (user_id, weight_kg, recorded_date)
                VALUES (%s, %s, %s)
                """,
                (
                    weight_entry.user_id,
                    weight_entry.weight_kg,
                    weight_entry.recorded_date,
                ),
            )
            weight_id = cursor.lastrowid
            connection.commit()
            return int(weight_id)
        except Exception:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
