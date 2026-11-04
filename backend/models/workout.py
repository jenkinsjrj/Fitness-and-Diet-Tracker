"""Workout data model and validation rules."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Workout:
    """A completed workout belonging to one application user."""

    user_id: int
    activity_type: str
    duration_minutes: int
    workout_date: date

    def validate(self) -> None:
        """Raise ValueError when the workout cannot be stored safely."""
        if type(self.user_id) is not int or self.user_id <= 0:
            raise ValueError("Invalid user ID")

        if not isinstance(self.activity_type, str):
            raise ValueError("Activity type must be text")
        self.activity_type = self.activity_type.strip()
        if not self.activity_type:
            raise ValueError("Activity type cannot be empty")
        if len(self.activity_type) > 100:
            raise ValueError("Activity type must be 100 characters or fewer")

        # bool is a subclass of int, so use an exact type check.
        if type(self.duration_minutes) is not int:
            raise ValueError("Duration must be an integer")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be positive")

        # A datetime is also a date subclass; this field is SQL DATE, not DATETIME.
        if type(self.workout_date) is not date:
            raise ValueError("Workout date must be a valid date")
