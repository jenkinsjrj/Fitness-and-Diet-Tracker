"""
Workout Class
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class Workout:
    user_id: int
    activity_type: str
    duration_minutes: int
    workout_date: date

    def validate(self):
        if self.user_id <= 0:
            raise ValueError("Invalid user ID")

        if not self.activity_type.strip():
            raise ValueError(
                "Activity type cannot be empty"
            )

        if self.duration_minutes <= 0:
            raise ValueError(
                "Duration must be positive"
            )
