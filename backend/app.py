
from flask import Flask, jsonify

from backend.routes.workout_routes import (
    workout_bp
)


def create_app():
    app = Flask(__name__)

    app.register_blueprint(workout_bp)

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

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
