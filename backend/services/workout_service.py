"""Business logic for workout logging."""

from backend.repositories.workout_repository import WorkoutRepository


class WorkoutService:
    """Validate and coordinate workout operations."""

    @staticmethod
    def get_workouts(user_id: int) -> list[dict]:
        workouts = WorkoutRepository.get_all(user_id)
        for workout in workouts:
            value = workout.get("workout_date")
            if hasattr(value, "isoformat"):
                workout["workout_date"] = value.isoformat()
        return workouts

    @staticmethod
    def add_workout(workout) -> int:
        workout.validate()
        return WorkoutRepository.create(workout)

    @staticmethod
    def delete_workout(user_id: int, workout_id: int) -> bool:
        if type(workout_id) is not int or workout_id <= 0:
            raise ValueError("Workout ID must be a positive integer")
        return WorkoutRepository.delete(user_id, workout_id)
