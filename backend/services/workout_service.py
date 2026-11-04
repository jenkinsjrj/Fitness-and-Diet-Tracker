"""
Workout Service

"""
from backend.repositories.workout_repository import (
    WorkoutRepository
)


class WorkoutService:

    @staticmethod
    def get_workouts(user_id):
        workouts = WorkoutRepository.get_all(user_id)

        for workout in workouts:
            workout["workout_date"] = (
                workout["workout_date"].isoformat()
            )

        return workouts

    @staticmethod
    def add_workout(workout):
        workout.validate()

        return WorkoutRepository.create(workout)
