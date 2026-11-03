
import mysql.connector
from flask import Flask, jsonify
from backend.db import get_db_connection

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({
        "message": "Fitness and Nutrition Tracker API",
        "status": "running"
    })


@app.get("/api/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.get("/api/workouts")
def get_workouts():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                user_id,
                activity_type,
                duration_minutes,
                workout_date
            FROM workouts
            ORDER BY workout_date DESC, id DESC
        """)

        workouts = cursor.fetchall()

        # Convert MySQL date objects to JSON strings.
        for workout in workouts:
            workout["workout_date"] = (
                workout["workout_date"].isoformat()
            )

        return jsonify(workouts), 200

    except mysql.connector.Error:
        app.logger.exception(
            "Failed to retrieve workouts"
        )

        return jsonify({
            "error": "Database operation failed"
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000) # FIXME: Set debug to false for final app
