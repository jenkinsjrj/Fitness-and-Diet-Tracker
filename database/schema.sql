
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    height_cm DECIMAL(5,2),
    goal_weight_kg DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS workouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    duration_minutes INT NOT NULL,
    workout_date DATE NOT NULL,

    FOREIGN KEY (user_id)
        REFERENCES users(id),

    CHECK (duration_minutes > 0)
);