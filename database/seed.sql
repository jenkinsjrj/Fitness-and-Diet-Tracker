/* EXAMPLE DATA
 *
 * This is meant to provide example data for testing and development
 * This createa a demo user who has completed three workouts, eaten one breakfast meal with
 * 1 serving of Oatmeal and 2 servings of Eggs
 */

/* * * * * * * * * *
 * CREATING A USER
 * * * * * * * * * */
INSERT INTO users
    (id, name, height_cm, goal_weight_kg, daily_calorie_target, weekly_workout_target)
VALUES
    (1, 'Demo User', 180.00, 80.00, 2500, 3);

/* * * * * * * * * *
 * CREATING A WORKOUT
 * * * * * * * * * */
INSERT INTO workouts
    (user_id, activity_type, duration_minutes, workout_date)
VALUES
    (1, 'Running', 30, '2026-11-01'),
    (1, 'Weightlifting', 45, '2026-11-02'),
    (1, 'Cycling', 60, '2026-11-03');

/* * * * * * * * * *
 * CREATING A WEIGHT RECORD
 * * * * * * * * * */
INSERT INTO weight_history (
    user_id, weight_kg, recorded_date
)
VALUES
    (1, 84.50, '2026-10-20'),
    (1, 83.80, '2026-10-27'),
    (1, 83.20, '2026-11-03');

/* * * * * * * * * *
 * ADDING A FOOD ITEM
 * * * * * * * * * */
INSERT INTO foods (
    name, serving_description,
    calories, protein_g, carbs_g, fat_g
)
VALUES
    ('Egg', '1 large egg', 72, 6.3, 0.4, 4.8),
    ('Oatmeal', '1 cup cooked', 154, 6, 27, 3),
    ('Chicken Breast', '100 g cooked', 165, 31, 0, 3.6),
    ('Brown Rice', '1 cup cooked', 216, 5, 45, 1.8),
    ('Banana', '1 medium banana', 105, 1.3, 27, 0.4);

/* * * * * * * * * *
 * CREATING A MEAL
 * * * * * * * * * *
 *
 * To create a meal, you must add a row to the meal table, as well as however
 * many food entries in the meal into meal_items rows
 * 
 * Steps:
 * 1. Insert meals row with user_id, meal_date, and meal_type
 */
-- Sample meal
INSERT INTO meals (
    user_id, meal_date, meal_type
)
VALUES
    (1, '2026-11-03', 'Breakfast');

/* 
 * 2. Insert individual meal_items using the meal_id using template below
 */
-- Link foods to the breakfast
INSERT INTO meal_items (
    meal_id, food_id, servings
)
SELECT m.id, f.id, 2
FROM meals m
JOIN foods f ON f.name = 'Egg'
WHERE m.user_id = 1
  AND m.meal_date = '2026-11-03'
  AND m.meal_type = 'Breakfast'
ORDER BY m.id
LIMIT 1;

INSERT INTO meal_items (
    meal_id, food_id, servings
)
SELECT m.id, f.id, 1
FROM meals m
JOIN foods f ON f.name = 'Oatmeal'
WHERE m.user_id = 1
  AND m.meal_date = '2026-11-03'
  AND m.meal_type = 'Breakfast'
ORDER BY m.id
LIMIT 1;

/* * * * * * * * * *
 * CREATING A REMINDER
 * * * * * * * * * *
 *
 * Follow template below
 */
INSERT INTO reminders (
    user_id, title, description, scheduled_at
)
VALUES (
    1,
    'Evening Workout',
    '30 minutes of running',
    '2026-11-06 22:00:00'
);