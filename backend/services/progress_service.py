"""Business logic for weight logging and fitness progress calculations."""

from datetime import timedelta
from decimal import Decimal

from backend.repositories.progress_repository import ProgressRepository
from backend.repositories.weight_repository import WeightRepository
from backend.repositories.workout_repository import WorkoutRepository


class ProgressService:
    """Coordinate weight history and calculate weekly/weight progress."""

    @staticmethod
    def add_weight(weight_entry) -> int:
        weight_entry.validate()
        return WeightRepository.create(weight_entry)

    @staticmethod
    def get_weight_history(user_id: int) -> list[dict]:
        records = WeightRepository.get_all(user_id)
        result = []
        for record in records:
            weight = record["weight_kg"]
            recorded_date = record["recorded_date"]
            result.append(
                {
                    "id": int(record["id"]),
                    "user_id": int(record["user_id"]),
                    "weight_kg": float(weight),
                    "recorded_date": (
                        recorded_date.isoformat()
                        if hasattr(recorded_date, "isoformat")
                        else str(recorded_date)
                    ),
                }
            )
        return result

    @staticmethod
    def _weight_goal_percentage(starting_weight, current_weight, goal_weight):
        """Return bounded progress from the first recorded weight toward the goal.

        Supports either a loss goal (start > goal) or gain goal (start < goal).
        Returns None when no baseline or no goal exists.
        """
        if starting_weight is None or current_weight is None or goal_weight is None:
            return None

        starting = Decimal(str(starting_weight))
        current = Decimal(str(current_weight))
        goal = Decimal(str(goal_weight))
        total_change_needed = starting - goal

        if total_change_needed == 0:
            return 100.0 if current == goal else 0.0

        percentage = ((starting - current) / total_change_needed) * Decimal("100")
        percentage = max(Decimal("0"), min(Decimal("100"), percentage))
        return round(float(percentage), 1)

    @staticmethod
    def get_progress(user_id: int, week_start) -> dict:
        """Return weekly workout totals and the user's weight trend.

        week_start must be a Monday. week_end is the following Sunday.
        """
        targets = ProgressRepository.get_user_targets(user_id)
        if targets is None:
            raise LookupError("User was not found")

        weekly_target = int(targets["weekly_workout_target"])
        week_end = week_start + timedelta(days=6)
        totals = WorkoutRepository.get_weekly_summary(user_id, week_start, week_end)
        workout_count = int(totals.get("workout_count") or 0)
        total_minutes = int(totals.get("total_minutes") or 0)
        percentage = round((workout_count / weekly_target) * 100, 1)

        raw_weights = WeightRepository.get_all(user_id)
        history = []
        for item in raw_weights:
            value = Decimal(str(item["weight_kg"]))
            measured_on = item["recorded_date"]
            history.append(
                {
                    "id": int(item["id"]),
                    "weight_kg": float(value),
                    "recorded_date": (
                        measured_on.isoformat()
                        if hasattr(measured_on, "isoformat")
                        else str(measured_on)
                    ),
                    "_weight_decimal": value,
                }
            )

        if history:
            starting_weight = history[0]["_weight_decimal"]
            current_weight = history[-1]["_weight_decimal"]
            weight_change = current_weight - starting_weight
            goal_weight = targets.get("goal_weight_kg")
            if goal_weight is not None:
                goal_weight = Decimal(str(goal_weight))
            weight_goal_percentage = ProgressService._weight_goal_percentage(
                starting_weight, current_weight, goal_weight
            )
            starting_weight_value = float(starting_weight)
            current_weight_value = float(current_weight)
            weight_change_value = float(weight_change)
        else:
            goal_weight = targets.get("goal_weight_kg")
            starting_weight_value = None
            current_weight_value = None
            weight_change_value = None
            weight_goal_percentage = None

        # Remove private calculation values before sending JSON to the frontend.
        public_history = [
            {key: value for key, value in item.items() if not key.startswith("_")}
            for item in history
        ]

        return {
            "user_id": user_id,
            "week": {
                "start_date": week_start.isoformat(),
                "end_date": week_end.isoformat(),
            },
            "workouts": {
                "count": workout_count,
                "total_minutes": total_minutes,
                "weekly_goal": weekly_target,
                "remaining": max(weekly_target - workout_count, 0),
                "goal_progress_percentage": percentage,
                "goal_met": workout_count >= weekly_target,
            },
            "weight": {
                "starting_weight_kg": starting_weight_value,
                "current_weight_kg": current_weight_value,
                "change_since_first_record_kg": weight_change_value,
                "goal_weight_kg": (
                    float(goal_weight) if goal_weight is not None else None
                ),
                "goal_progress_percentage": weight_goal_percentage,
                "record_count": len(public_history),
                "history": public_history,
            },
        }
