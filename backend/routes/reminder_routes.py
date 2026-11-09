
import mysql.connector
from flask import Blueprint, jsonify, request

from backend.services.reminder_service import (
    ReminderService
)

reminder_bp = Blueprint(
    "reminders",
    __name__,
    url_prefix="/api/reminders"
)

# Milestone 1 uses the predefined demonstration user.
DEMO_USER_ID = 1


@reminder_bp.get("")
def list_reminders():
    try:
        reminders = ReminderService.get_reminders(
            DEMO_USER_ID,
            request.args.get("date")
        )
        return jsonify(reminders), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except mysql.connector.Error:
        return jsonify({
            "error": "Unable to retrieve reminders"
        }), 500


@reminder_bp.get("/<int:reminder_id>")
def get_reminder(reminder_id):
    try:
        reminder = ReminderService.get_reminder(
            reminder_id, DEMO_USER_ID
        )

        if reminder is None:
            return jsonify({
                "error": "Reminder not found"
            }), 404

        return jsonify(reminder), 200

    except mysql.connector.Error:
        return jsonify({
            "error": "Unable to retrieve reminder"
        }), 500


@reminder_bp.post("")
def create_reminder():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    try:
        reminder_id = ReminderService.create_reminder(
            DEMO_USER_ID, data
        )

        reminder = ReminderService.get_reminder(
            reminder_id, DEMO_USER_ID
        )

        return jsonify(reminder), 201

    except (KeyError, TypeError, ValueError) as error:
        return jsonify({
            "error": str(error)
        }), 400

    except mysql.connector.Error:
        return jsonify({
            "error": "Unable to create reminder"
        }), 500


@reminder_bp.patch("/<int:reminder_id>")
def update_reminder(reminder_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    try:
        updated = ReminderService.update_reminder(
            reminder_id, DEMO_USER_ID, data
        )

        if not updated:
            return jsonify({
                "error": "Reminder not found"
            }), 404

        reminder = ReminderService.get_reminder(
            reminder_id, DEMO_USER_ID
        )

        return jsonify(reminder), 200

    except (TypeError, ValueError) as error:
        return jsonify({
            "error": str(error)
        }), 400

    except mysql.connector.Error:
        return jsonify({
            "error": "Unable to update reminder"
        }), 500


@reminder_bp.delete("/<int:reminder_id>")
def delete_reminder(reminder_id):
    try:
        deleted = ReminderService.delete_reminder(
            reminder_id, DEMO_USER_ID
        )

        if not deleted:
            return jsonify({
                "error": "Reminder not found"
            }), 404

        return "", 204

    except mysql.connector.Error:
        return jsonify({
            "error": "Unable to delete reminder"
        }), 500
