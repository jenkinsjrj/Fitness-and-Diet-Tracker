# Maxim — Milestone 1: Workout Logging and Progress Tracking

This folder contains the implementation for Maxim's assigned backend features. It follows the project's existing Flask + MySQL structure and uses the existing `workouts`, `weight_history`, and `users` tables. **No SQL schema change is required** for these features.

## Included endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/workouts` | Validate and save a workout |
| `GET` | `/api/workouts` | List the demonstration user's workouts |
| `DELETE` | `/api/workouts/<id>` | Delete one of that user's workouts |
| `POST` | `/api/weights` | Save a body-weight measurement in kilograms |
| `GET` | `/api/weights` | Retrieve body-weight history, oldest first |
| `GET` | `/api/progress` | Calculate weekly workout totals and weight progress |

The application currently uses the predefined demonstration user with ID `1`, consistent with the initial backend plan. There is no authentication or user-selection feature yet. The `DEFAULT_USER_ID` Flask setting makes this easy to change for the optional integration test.

## Request examples

Create a workout:

```http
POST /api/workouts
Content-Type: application/json

{
  "activity_type": "Running",
  "duration_minutes": 30,
  "workout_date": "2026-11-04"
}
```

Record body weight (all stored/displayed weight values use kilograms):

```http
POST /api/weights
Content-Type: application/json

{
  "weight_kg": 83.2,
  "recorded_date": "2026-11-04"
}
```

Get progress for a particular week:

```http
GET /api/progress?week_start=2026-11-02
```

`week_start` is optional. When omitted, the API uses the current Monday. When supplied, it must be a Monday in `YYYY-MM-DD` format. The returned week runs Monday through Sunday. Weekly completion is `workout_count / weekly_workout_target * 100`; `remaining` never falls below zero. The weight summary compares the earliest recorded weight with the latest recorded weight and, when a target weight exists, reports bounded progress from the starting value toward that goal. A missing history or goal produces `null` for metrics that cannot be calculated.

## Validation and error behavior

- Workout activity must be nonempty text and no longer than 100 characters.
- Workout duration must be a positive integer number of minutes.
- Workout and weight dates must be exactly `YYYY-MM-DD`.
- Weight must be a positive finite number, no greater than `999.99`, with at most two decimal places, matching `DECIMAL(5,2)` in `schema.sql`.
- Invalid request data returns HTTP `400`; missing workout IDs/users return `404`; database failures return a generic HTTP `500` response and are logged by Flask.
- SQL statements use parameter placeholders rather than string interpolation.

## Run and test

Run commands from the repository root. The MySQL container must be running and the existing schema/seed setup must have completed before starting the API.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.app
```

In another terminal, run the fast tests. They use an in-memory fake repository, so they do not require MySQL:

```powershell
python -m pytest -q
```

For an additional check against the real MySQL tables, start Docker/MySQL using the team's README procedure, then run:

```powershell
$env:RUN_MYSQL_INTEGRATION = "1"
python -m pytest -q tests/test_mysql_integration.py
```

The integration test creates a temporary user and removes its workouts, weight records, and user when finished. Do not point it at a shared production database.

## Files to copy

Copy the `backend/` folder in this package into the repository root, replacing the existing `backend/` files, and copy `tests/` into the repository root (merge with any existing tests instead of deleting teammates' tests). The existing `schema.sql` already contains every column used here. Keep the team's existing `db.py` connection configuration and `.env` file; this package includes the current `db.py` interface only as an integration dependency, not as a required change.

## Verification notes for the milestone report

The automated API tests cover successful workout creation/listing/deletion, invalid workout input, weight creation/history retrieval, weekly workout totals, weight change/goal progress, and invalid week selection. Run the optional MySQL integration test and record its actual result before claiming database persistence has been verified. Also make a substantive commit for this implementation during the milestone period and save this AI-assisted development conversation in the project's `ai/` folder, with the student/tool/date and a brief explanation of how the code and tests were reviewed.
