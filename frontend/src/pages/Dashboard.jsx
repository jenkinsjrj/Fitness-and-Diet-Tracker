
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

import { api } from "../services/api";
import "./Dashboard.css";

export default function Dashboard() {
  const [progress, setProgress] = useState(null);
  const [nutrition, setNutrition] = useState(null);
  const [workouts, setWorkouts] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    async function loadDashboard() {
      // Get today's date in local time.
      const now = new Date();
      const today = [
        now.getFullYear(),
        String(now.getMonth() + 1).padStart(2, "0"),
        String(now.getDate()).padStart(2, "0")
      ].join("-");

      const results = await Promise.allSettled([
        api.getProgress(),
        api.getNutrition(today),
        api.getWorkouts(),
        api.getReminders()
      ]);

      const setters = [
        setProgress,
        setNutrition,
        setWorkouts,
        setReminders
      ];

      const names = [
        "Progress",
        "Nutrition",
        "Workouts",
        "Reminders"
      ];

      const failures = [];

      results.forEach((result, index) => {
        if (result.status === "fulfilled") {
          setters[index](result.value);
        } else {
          failures.push(
            `${names[index]}: ${result.reason.message}`
          );
        }
      });

      setErrors(failures);
      setLoading(false);
    }

    loadDashboard();
  }, []);

  if (loading) {
    return <p>Loading dashboard...</p>;
  }

  const weight = progress?.weight;
  const weekly = progress?.workouts;

  const weightHistory = weight?.history ?? [];

  const recentWorkouts = [...workouts]
    .sort((a, b) =>
      b.workout_date.localeCompare(a.workout_date)
    )
    .slice(0, 5);

  const upcomingReminders = reminders
    .filter((reminder) =>
      !reminder.completed &&
      new Date(reminder.scheduled_at) >= new Date()
    )
    .sort((a, b) =>
      new Date(a.scheduled_at) -
      new Date(b.scheduled_at)
    )
    .slice(0, 5);

  const formatNumber = (value, digits = 0) =>
    value == null ? "—" : Number(value).toFixed(digits);

  const formatDate = (value) => {
    if (!value) return "";
    return new Date(`${value}T12:00:00`).toLocaleDateString();
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>Your fitness and nutrition overview</p>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="dashboard-error" role="alert">
          <strong>Some information could not be loaded.</strong>
          {errors.map((error) => (
            <p key={error}>{error}</p>
          ))}
        </div>
      )}

      {/* Summary cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <span>Current Weight</span>
          <h2>
            {formatNumber(weight?.current_weight_kg, 1)}
            <small> kg</small>
          </h2>
          <p>
            Goal: {formatNumber(weight?.goal_weight_kg, 1)} kg
          </p>
        </div>

        <div className="stat-card">
          <span>Calories Today</span>
          <h2>
            {formatNumber(nutrition?.calories)}
            <small> kcal</small>
          </h2>
          <p>
            {formatNumber(nutrition?.remaining_calories)}
            {" "}remaining
          </p>
        </div>

        <div className="stat-card">
          <span>Workouts This Week</span>
          <h2>
            {weekly?.count ?? "—"}
            <small> / {weekly?.weekly_goal ?? "—"}</small>
          </h2>
          <p>
            {formatNumber(weekly?.goal_progress_percentage, 1)}%
            {" "}of weekly goal
          </p>
        </div>

        <div className="stat-card">
          <span>Workout Minutes</span>
          <h2>
            {weekly?.total_minutes ?? "—"}
            <small> min</small>
          </h2>
          <p>This week</p>
        </div>
      </div>

      {/* Weight progress */}
      <div className="dashboard-card">
        <div className="card-header">
          <h2>Weight Progress</h2>
          <Link to="/progress">View Progress</Link>
        </div>

        {weightHistory.length > 0 ? (
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={weightHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="recorded_date" />
                <YAxis
                  domain={["auto", "auto"]}
                  width={45}
                />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="weight_kg"
                  stroke="#16a34a"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  name="Weight (kg)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p>No weight entries recorded yet.</p>
        )}

        {weight && (
          <p className="muted">
            Weight change since first record:{" "}
            {formatNumber(
              weight.change_since_first_record_kg, 1
            )} kg
          </p>
        )}
      </div>

      {/* Nutrition summary */}
      <div className="dashboard-card">
        <div className="card-header">
          <h2>Daily Nutrition</h2>
          <Link to="/nutrition">View Nutrition</Link>
        </div>

        {nutrition ? (
          <>
            <p>
              {formatNumber(nutrition.calories)} /{" "}
              {formatNumber(nutrition.daily_calorie_target)}
              {" "}calories
            </p>

            <progress
              value={Math.min(
                Math.max(nutrition.calories, 0),
                Math.max(nutrition.daily_calorie_target, 1)
              )}
              max={Math.max(
                nutrition.daily_calorie_target, 1
              )}
              className="calorie-progress"
            />

            <div className="macro-grid">
              <div>
                <strong>
                  {formatNumber(nutrition.protein_g, 1)}g
                </strong>
                <span>Protein</span>
              </div>
              <div>
                <strong>
                  {formatNumber(nutrition.carbs_g, 1)}g
                </strong>
                <span>Carbs</span>
              </div>
              <div>
                <strong>
                  {formatNumber(nutrition.fat_g, 1)}g
                </strong>
                <span>Fat</span>
              </div>
            </div>
          </>
        ) : (
          <p>Nutrition data unavailable.</p>
        )}
      </div>

      {/* Workouts and reminders */}
      <div className="dashboard-bottom-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h2>Recent Workouts</h2>
            <Link to="/workouts">View All</Link>
          </div>

          {recentWorkouts.length === 0 ? (
            <p>No workouts recorded.</p>
          ) : (
            recentWorkouts.map((workout) => (
              <div className="dashboard-list-item" key={workout.id}>
                <div>
                  <strong>{workout.activity_type}</strong>
                  <p>{formatDate(workout.workout_date)}</p>
                </div>
                <span>{workout.duration_minutes} min</span>
              </div>
            ))
          )}
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h2>Upcoming Reminders</h2>
            <Link to="/calendar">View Calendar</Link>
          </div>

          {upcomingReminders.length === 0 ? (
            <p>No upcoming reminders.</p>
          ) : (
            upcomingReminders.map((reminder) => (
              <div className="dashboard-list-item" key={reminder.id}>
                <div>
                  <strong>{reminder.title}</strong>
                  <p>
                    {new Date(
                      reminder.scheduled_at
                    ).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
