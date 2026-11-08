"""Flask application entry point for the Fitness and Nutrition Tracker."""

from flask import Flask, jsonify

from backend.routes.nutrition_routes import nutrition_bp
from backend.routes.progress_routes import progress_bp
from backend.routes.workout_routes import workout_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(DEFAULT_USER_ID=1)
    if test_config:
        app.config.update(test_config)

    # Maxim's feature blueprints: workout logging and progress tracking.
    app.register_blueprint(workout_bp)
    app.register_blueprint(progress_bp)

    # Trent's features: nutrition tracking and food recommendations.
    app.register_blueprint(nutrition_bp)

    @app.get("/")
    def home():
        return jsonify(
            {
                "message": "Fitness and Nutrition Tracker API",
                "status": "running",
            }
        )

    @app.get("/api/health")
    def health():
        return jsonify({"status": "healthy"})

    return app


app = create_app()


if __name__ == "__main__":
    # Debug mode is intended for local development only.
    app.run(debug=True, port=5000)
