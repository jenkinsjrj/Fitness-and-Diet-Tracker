"""HTTP endpoints for workout logging."""

import mysql.connector
from flask import Blueprint, current_app, jsonify, request

from backend.models.workout import Workout
from backend.services.workout_service import WorkoutService
from backend.routes.validators import parse_iso_date


workout_bp = Blueprint("workouts", __name__, url_prefix="/api/workouts")


def _user_id() -> int:
    # This project currently uses one predefined demo user; there is no login system.
    return int(current_app.config["DEFAULT_USER_ID"])


@workout_bp.get("")
def get_workouts():
    try:
        return jsonify(WorkoutService.get_workouts(_user_id())), 200
    except mysql.connector.Error:
        current_app.logger.exception("Database error while retrieving workouts")
        return jsonify({"error": "Unable to retrieve workouts"}), 500


@workout_bp.post("")
def create_workout():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        workout = Workout(
            user_id=_user_id(),
            activity_type=data.get("activity_type"),
            duration_minutes=data.get("duration_minutes"),
            workout_date=parse_iso_date(data.get("workout_date"), "workout_date"),
        )
        workout_id = WorkoutService.add_workout(workout)
        return jsonify(
            {
                "message": "Workout created",
                "workout": {
                    "id": workout_id,
                    "user_id": workout.user_id,
                    "activity_type": workout.activity_type,
                    "duration_minutes": workout.duration_minutes,
                    "workout_date": workout.workout_date.isoformat(),
                },
            }
        ), 201
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    except mysql.connector.Error:
        current_app.logger.exception("Database error while saving workout")
        return jsonify({"error": "Unable to save workout"}), 500


@workout_bp.delete("/<int:workout_id>")
def delete_workout(workout_id: int):
    try:
        deleted = WorkoutService.delete_workout(_user_id(), workout_id)
        if not deleted:
            return jsonify({"error": "Workout not found"}), 404
        return jsonify({"message": "Workout deleted", "id": workout_id}), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except mysql.connector.Error:
        current_app.logger.exception("Database error while deleting workout")
        return jsonify({"error": "Unable to delete workout"}), 500
