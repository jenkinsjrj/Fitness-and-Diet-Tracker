
from datetime import datetime, date, time, timedelta, timezone

from backend.models.reminder import Reminder
from backend.repositories.reminder_repository import (
    ReminderRepository
)


class ReminderService:

    @staticmethod
    def parse_datetime(value):
        if not isinstance(value, str):
            raise ValueError("Date must be an ISO 8601 string")

        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            raise ValueError("Invalid date format")

        if parsed.tzinfo is None:
            raise ValueError("Date must include a timezone")

        return parsed.astimezone(timezone.utc)

    @staticmethod
    def format_reminder(row):
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "title": row["title"],
            "description": row["description"],
            "scheduled_at": (
                row["scheduled_at"]
                .replace(tzinfo=timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            ),
            "completed": bool(row["completed"])
        }

    @staticmethod
    def get_reminders(user_id, date_filter=None):
        start = None
        end = None

        if date_filter:
            try:
                selected = date.fromisoformat(date_filter)
            except (TypeError, ValueError):
                raise ValueError("Date must use YYYY-MM-DD")

            start = datetime.combine(selected, time.min)
            end = start + timedelta(days=1)

        rows = ReminderRepository.get_all(
            user_id, start, end
        )

        return [
            ReminderService.format_reminder(row)
            for row in rows
        ]

    @staticmethod
    def get_reminder(reminder_id, user_id):
        row = ReminderRepository.get_by_id(
            reminder_id, user_id
        )

        if row is None:
            return None

        return ReminderService.format_reminder(row)

    @staticmethod
    def create_reminder(user_id, data):
        reminder = Reminder(
            user_id=user_id,
            title=data["title"],
            description=data.get("description", ""),
            scheduled_at=ReminderService.parse_datetime(
                data["scheduled_at"]
            )
        )

        reminder.validate()
        return ReminderRepository.create(reminder)

    @staticmethod
    def update_reminder(reminder_id, user_id, data):
        existing = ReminderRepository.get_by_id(
            reminder_id, user_id
        )

        if existing is None:
            return False

        scheduled_at = (
            ReminderService.parse_datetime(data["scheduled_at"])
            if "scheduled_at" in data
            else existing["scheduled_at"].replace(
                tzinfo=timezone.utc
            )
        )

        reminder = Reminder(
            user_id=user_id,
            title=data.get("title", existing["title"]),
            description=data.get(
                "description", existing["description"] or ""
            ),
            scheduled_at=scheduled_at,
            completed=data.get(
                "completed", bool(existing["completed"])
            )
        )

        reminder.validate()

        ReminderRepository.update(
            reminder_id, user_id, reminder
        )
        return True

    @staticmethod
    def delete_reminder(reminder_id, user_id):
        return ReminderRepository.delete(
            reminder_id, user_id
        )
