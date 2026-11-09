/* schema.sql
 * 
 * Describes the SQL database's 8 tables consisting of:
 * - users
 * - workouts
 * - weight_history
 * - foods
 * - meals
 * - meal_items
 * - reminders
 * 
 * 
 */

/* * * * * * * * * *
 * USERS TABLE     
 * * * * * * * * * *
 * 
 * Table Columns:
 * id - unique id 
 * height_cm - height in cm
 * goal_weight - Desired weight to get to
 * daily_calorie_target - target for daily caloric intake
 * weekly_workout_target - target number of workouts per week
 *
 * Note that current and past weight entries are stored in the weight_history table, and
 * thus current weight is intentionally not stored in the users table 
 * 
 */

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    height_cm DECIMAL(5,2),
    goal_weight_kg DECIMAL(5,2),
    daily_calorie_target INT NOT NULL,
    weekly_workout_target INT NOT NULL,

    CHECK (daily_calorie_target > 0),
    CHECK (weekly_workout_target > 0)
);

/* * * * * * * * * *
 * WORKOUTS TABLE  
 * * * * * * * * * *
 * 
 * Table Columns:
 * id - unique id 
 * user_id - Foreign key to a user defined by their user_id
 * activity_type - Name of workout activity
 * duration_minutes - Duration of the workout
 * workout_date - date of the workout as YEAR-MM-DD (SQL DATE)
 */
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

/* * * * * * * * * *
 * WEIGHT_HISTORY TABLE  
 * * * * * * * * * *
 * 
 * Table Columns:
 * id - unique id 
 * user_id - Foreign key to a user defined by their user_id
 * weight_kg - The recorded weight in kilograms
 * recorded_date - The date of the entry as YEAR-MM-DD (SQL DATE)
 */
CREATE TABLE IF NOT EXISTS weight_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    recorded_date DATE NOT NULL,

    FOREIGN KEY (user_id)
        REFERENCES users(id),

    CHECK (weight_kg > 0)
);

-- FOOD AND NUTRITION DATABASES

/* * * * * * * * * *
 * FOODS TABLE  
 * * * * * * * * * *
 * 
 * Table Columns:
 * id - unique id 
 * name - food name
 * serving_description - description of how a food serving is defined (ex. "1 cup")
 * calories - number of calories in one serving
 * protein_g - amount of protein in one serving in grams
 * carbs_g - amount of carbs in one serving in grams
 * fat_g - amount of fat in one serving in grams
 */
CREATE TABLE IF NOT EXISTS foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    serving_description VARCHAR(100) NOT NULL,
    calories DECIMAL(8,2) NOT NULL,
    protein_g DECIMAL(8,2) NOT NULL,
    carbs_g DECIMAL(8,2) NOT NULL,
    fat_g DECIMAL(8,2) NOT NULL,

    CHECK (calories >= 0),
    CHECK (protein_g >= 0),
    CHECK (carbs_g >= 0),
    CHECK (fat_g >= 0)
);

/* * * * * * * * * *
 * MEALS TABLE
 * * * * * * * * * *
 * 
 * Table Columns:
 * id - unique id 
 * user_id - Foreign key to a user defined by their user_id
 * meal_type - Breakfast/Lunch/Dinner
 * meal_date - The date of the meal as YEAR-MM-DD (SQL DATE)
 */
CREATE TABLE IF NOT EXISTS meals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    meal_type VARCHAR(30) NOT NULL,
    meal_date DATE NOT NULL,
    

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);

/* * * * * * * * * *
 * MEAL_ITEMS TABLE
 * * * * * * * * * *
 * 
 * Table Columns:
 * id - unique id 
 * meal_id - Foreign key to a meal defined by its meal_id
 * food_id - The food item that was eaten by food_id
 * servings - number of serving of the food item that was consumed
 */
CREATE TABLE IF NOT EXISTS meal_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meal_id INT NOT NULL,
    food_id INT NOT NULL,
    servings DECIMAL(6,2) NOT NULL,

    FOREIGN KEY (meal_id)
        REFERENCES meals(id)
        ON DELETE CASCADE,

    FOREIGN KEY (food_id)
        REFERENCES foods(id),

    CHECK (servings > 0)
);


/* * * * * * * * * *
 * REMINDERS TABLE 
 * * * * * * * * * *
 * 
 * Table Columns:
 * id - unique id 
 * user_id - Foreign key to a user defined by their user_id
 * title - Title for the reminder
 * description - Description of the reminder
 * scheduled_at - The date the reminder is set to as YYYY-MM-DD HH:MM:SS (SQL DATETIME)
 * completed - To keep track of reminder status
 */
CREATE TABLE IF NOT EXISTS reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    scheduled_at DATETIME NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
