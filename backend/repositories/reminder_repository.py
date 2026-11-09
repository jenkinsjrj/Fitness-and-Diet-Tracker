
from backend.db import get_db_connection, execute_select


class ReminderRepository:

    @staticmethod
    def get_all(user_id, start=None, end=None):
        query = """
            SELECT id, user_id, title, description,
                   scheduled_at, completed
            FROM reminders
            WHERE user_id = %s
        """
        params = [user_id]

        if start is not None:
            query += " AND scheduled_at >= %s"
            params.append(start)

        if end is not None:
            query += " AND scheduled_at < %s"
            params.append(end)

        query += " ORDER BY scheduled_at, id"

        return execute_select(query, tuple(params))

    @staticmethod
    def get_by_id(reminder_id, user_id):
        rows = execute_select(
            """
            SELECT id, user_id, title, description,
                   scheduled_at, completed
            FROM reminders
            WHERE id = %s AND user_id = %s
            """,
            (reminder_id, user_id)
        )
        return rows[0] if rows else None

    @staticmethod
    def create(reminder):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO reminders
                    (user_id, title, description,
                     scheduled_at, completed)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    reminder.user_id,
                    reminder.title,
                    reminder.description,
                    reminder.scheduled_at.replace(
                        tzinfo=None
                    ),
                    reminder.completed
                )
            )
            reminder_id = cursor.lastrowid
            connection.commit()
            return reminder_id

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    @staticmethod
    def update(reminder_id, user_id, reminder):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE reminders
                SET title = %s,
                    description = %s,
                    scheduled_at = %s,
                    completed = %s
                WHERE id = %s AND user_id = %s
                """,
                (
                    reminder.title,
                    reminder.description,
                    reminder.scheduled_at.replace(
                        tzinfo=None
                    ),
                    reminder.completed,
                    reminder_id,
                    user_id
                )
            )
            updated = cursor.rowcount > 0
            connection.commit()
            return updated

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    @staticmethod
    def delete(reminder_id, user_id):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                DELETE FROM reminders
                WHERE id = %s AND user_id = %s
                """,
                (reminder_id, user_id)
            )
            deleted = cursor.rowcount > 0
            connection.commit()
            return deleted

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
