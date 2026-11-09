
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Reminder:
    user_id: int
    title: str
    scheduled_at: datetime
    description: str = ""
    completed: bool = False

    def validate(self):
        if type(self.user_id) is not int or self.user_id <= 0:
            raise ValueError("Invalid user ID")

        if not isinstance(self.title, str):
            raise ValueError("Title must be text")

        self.title = self.title.strip()

        if not self.title:
            raise ValueError("Title cannot be empty")

        if len(self.title) > 150:
            raise ValueError("Title cannot exceed 150 characters")

        if not isinstance(self.description, str):
            raise ValueError("Description must be text")

        if not isinstance(self.scheduled_at, datetime):
            raise ValueError("Invalid scheduled date")

        if self.scheduled_at.tzinfo is None:
            raise ValueError("Scheduled date must include a timezone")

        self.scheduled_at = self.scheduled_at.astimezone(
            timezone.utc
        )

        if type(self.completed) is not bool:
            raise ValueError("Completed must be a boolean")
