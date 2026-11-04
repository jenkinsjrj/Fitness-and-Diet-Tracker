"""HTTP endpoints for body-weight history and progress tracking."""

import mysql.connector
from datetime import date, timedelta
from flask import Blueprint, current_app, jsonify, request

from backend.models.weight_entry import WeightEntry
from backend.routes.validators import parse_iso_date
from backend.services.progress_service import ProgressService


progress_bp = Blueprint("progress", __name__, url_prefix="/api")


def _user_id() -> int:
    # Same predefined demonstration user as the workout endpoints.
    return int(current_app.config["DEFAULT_USER_ID"])


@progress_bp.post("/weights")
def create_weight_entry():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        entry = WeightEntry(
            user_id=_user_id(),
            weight_kg=data.get("weight_kg"),
            recorded_date=parse_iso_date(data.get("recorded_date"), "recorded_date"),
        )
        weight_id = ProgressService.add_weight(entry)
        return jsonify(
            {
                "message": "Weight recorded",
                "weight": {
                    "id": weight_id,
                    "user_id": entry.user_id,
                    "weight_kg": float(entry.weight_kg),
                    "recorded_date": entry.recorded_date.isoformat(),
                },
            }
        ), 201
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    except mysql.connector.Error:
        current_app.logger.exception("Database error while recording weight")
        return jsonify({"error": "Unable to record weight"}), 500


@progress_bp.get("/weights")
def get_weight_history():
    try:
        return jsonify(ProgressService.get_weight_history(_user_id())), 200
    except mysql.connector.Error:
        current_app.logger.exception("Database error while retrieving weight history")
        return jsonify({"error": "Unable to retrieve weight history"}), 500


@progress_bp.get("/progress")
def get_progress():
    try:
        week_start_value = request.args.get("week_start")
        if week_start_value is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        else:
            week_start = parse_iso_date(week_start_value, "week_start")

        if week_start.weekday() != 0:
            return jsonify(
                {"error": "week_start must be a Monday (YYYY-MM-DD)"}
            ), 400

        progress = ProgressService.get_progress(_user_id(), week_start)
        return jsonify(progress), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except LookupError as error:
        return jsonify({"error": str(error)}), 404
    except mysql.connector.Error:
        current_app.logger.exception("Database error while calculating progress")
        return jsonify({"error": "Unable to calculate progress"}), 500
