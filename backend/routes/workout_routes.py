
from datetime import date

import mysql.connector
from flask import Blueprint, jsonify, request

from backend.models.workout import Workout
from backend.services.workout_service import (
    WorkoutService
)

workout_bp = Blueprint(
    "workouts",
    __name__,
    url_prefix="/api/workouts"
)


@workout_bp.get("")
def get_workouts():
    try:
        workouts = WorkoutService.get_workouts(
            user_id=1
        )

        return jsonify(workouts), 200

    except mysql.connector.Error:
        return jsonify({
            "error": "Unable to retrieve workouts"
        }), 500


@workout_bp.post("")
def create_workout():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "A JSON object is required"
            }), 400

        duration = data["duration_minutes"]

        if type(duration) is not int:
            raise ValueError(
                "Duration must be an integer"
            )

        activity_type = data["activity_type"]

        if not isinstance(activity_type, str):
            raise ValueError(
                "Activity type must be text"
            )

        workout_date = date.fromisoformat(
            data["workout_date"]
        )

        workout = Workout(
            user_id=1,
            activity_type=activity_type,
            duration_minutes=duration,
            workout_date=workout_date
        )

        workout_id = WorkoutService.add_workout(
            workout
        )

        return jsonify({
            "message": "Workout created",
            "id": workout_id
        }), 201

    except (KeyError, ValueError, TypeError) as error:
        return jsonify({
            "error": str(error)
        }), 400

    except mysql.connector.Error:
        return jsonify({
            "error": "Unable to save workout"
        }), 500
