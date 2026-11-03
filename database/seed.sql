
INSERT INTO users
    (id, name, height_cm, goal_weight_kg)
VALUES
    (1, 'Demo User', 180.00, 80.00);

INSERT INTO workouts
    (user_id, activity_type, duration_minutes, workout_date)
VALUES
    (1, 'Running', 30, '2026-11-01'),
    (1, 'Weightlifting', 45, '2026-11-02'),
    (1, 'Cycling', 60, '2026-11-03');