import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../services/api";
import "./Progress.css";

function formatLocalDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function parseLocalDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function getMonday(date = new Date()) {
  const monday = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7));
  return monday;
}

function shiftDate(value, days) {
  const date = parseLocalDate(value);
  date.setDate(date.getDate() + days);
  return formatLocalDate(date);
}

function formatDate(value, options = {}) {
  if (!value) return "—";
  const date = parseLocalDate(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString([], {
        month: "short",
        day: "numeric",
        ...options,
      });
}

function formatWeight(value) {
  return value == null || Number.isNaN(Number(value))
    ? "—"
    : Number(value).toFixed(1);
}

function formatSigned(value) {
  if (value == null || Number.isNaN(Number(value))) return "—";
  const number = Number(value);
  return `${number > 0 ? "+" : ""}${number.toFixed(1)} kg`;
}

export default function Progress() {
  const [progress, setProgress] = useState(null);
  const [weekStart, setWeekStart] = useState(() => formatLocalDate(getMonday()));
  const [weight, setWeight] = useState("");
  const [recordedDate, setRecordedDate] = useState(formatLocalDate(new Date()));
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let active = true;

    async function loadProgress() {
      setLoading(true);
      setError("");
      try {
        const data = await api.getProgress(weekStart);
        if (active) setProgress(data);
      } catch (err) {
        if (active) setError(err.message || "Unable to load progress.");
      } finally {
        if (active) setLoading(false);
      }
    }

    loadProgress();
    return () => {
      active = false;
    };
  }, [weekStart]);

  const workouts = progress?.workouts;
  const weightProgress = progress?.weight;
  const history = weightProgress?.history ?? [];

  const currentWeekStart = formatLocalDate(getMonday());
  const canGoForward = weekStart < currentWeekStart;
  const percentage = Number(workouts?.goal_progress_percentage ?? 0);
  const workoutProgressWidth = Math.min(Math.max(percentage, 0), 100);
  const weightPercentage = weightProgress?.goal_progress_percentage;
  const weightProgressWidth = Math.min(
    Math.max(Number(weightPercentage ?? 0), 0),
    100
  );

  const chartData = history;

  async function handleWeightSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const value = Number(weight);
    if (!Number.isFinite(value) || value <= 0 || value > 999.99) {
      setError("Enter a weight greater than 0 and no more than 999.99 kg.");
      return;
    }
    if (Number(value.toFixed(2)) !== value) {
      setError("Weight can have at most two decimal places.");
      return;
    }
    if (!recordedDate) {
      setError("Please select the date of the measurement.");
      return;
    }

    try {
      setSaving(true);
      await api.addWeight({
        weight_kg: value,
        recorded_date: recordedDate,
      });
      setWeight("");
      setSuccess("Weight entry saved successfully.");
      try {
        const data = await api.getProgress(weekStart);
        setProgress(data);
      } catch (err) {
        setError(`Weight was saved, but progress could not be refreshed: ${err.message}`);
      }
    } catch (err) {
      setError(err.message || "Unable to save weight entry.");
    } finally {
      setSaving(false);
    }
  }

  function changeWeek(offset) {
    setWeekStart((current) => shiftDate(current, offset * 7));
  }

  return (
    <div className="progress-page">
      <header className="progress-header">
        <div>
          <h1>Progress Tracking</h1>
          <p>Monitor your workout goals and track changes in your weight.</p>
        </div>
        <div className="progress-week-picker" aria-label="Select week">
          <button
            type="button"
            className="progress-week-button"
            onClick={() => changeWeek(-1)}
            aria-label="Previous week"
          >
            ‹
          </button>
          <span>
            {formatDate(weekStart, { year: "numeric" })} – {formatDate(shiftDate(weekStart, 6), { year: "numeric" })}
          </span>
          <button
            type="button"
            className="progress-week-button"
            onClick={() => changeWeek(1)}
            disabled={!canGoForward}
            aria-label="Next week"
          >
            ›
          </button>
        </div>
      </header>

      {error && <div className="progress-error" role="alert">{error}</div>}
      {success && <div className="progress-success" role="status">{success}</div>}

      <section className="progress-stats-grid" aria-label="Progress summary">
        <article className="progress-stat-card">
          <span>Workouts This Week</span>
          <strong>
            {loading ? "—" : workouts?.count ?? 0}
            <small> / {workouts?.weekly_goal ?? "—"}</small>
          </strong>
          <p>{workouts?.total_minutes ?? 0} total minutes</p>
        </article>
        <article className="progress-stat-card">
          <span>Current Weight</span>
          <strong>{formatWeight(weightProgress?.current_weight_kg)}<small> kg</small></strong>
          <p>{weightProgress?.record_count ?? 0} measurements recorded</p>
        </article>
        <article className="progress-stat-card">
          <span>Change Since First Entry</span>
          <strong>
            {formatSigned(weightProgress?.change_since_first_record_kg)}
          </strong>
          <p>Based on your recorded weight history</p>
        </article>
      </section>

      <section className="card progress-workout-card">
        <div className="progress-card-heading">
          <div>
            <h2>Weekly Workout Goal</h2>
            <p className="progress-section-description">
              {progress?.week
                ? `${formatDate(progress.week.start_date, { year: "numeric" })} – ${formatDate(progress.week.end_date, { year: "numeric" })}`
                : "Your weekly workout summary"}
            </p>
          </div>
          <strong className="progress-goal-percent">
            {loading ? "—" : `${percentage.toFixed(1)}%`}
          </strong>
        </div>
        <div
          className="progress-goal-track"
          role="progressbar"
          aria-label="Weekly workout goal progress"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={workoutProgressWidth}
        >
          <span style={{ width: `${workoutProgressWidth}%` }} />
        </div>
        <div className="progress-goal-details">
          <span>{workouts?.count ?? 0} of {workouts?.weekly_goal ?? "—"} workouts completed</span>
          <span>
            {workouts?.goal_met
              ? "Goal completed"
              : `${workouts?.remaining ?? "—"} remaining`}
          </span>
        </div>
      </section>

      <section className="card progress-chart-card">
        <div className="progress-card-heading">
          <div>
            <h2>Weight Progress</h2>
            <p className="progress-section-description">
              Your recorded weight over time (kilograms)
            </p>
          </div>
          {weightProgress?.goal_weight_kg != null && (
            <div className="progress-weight-goal">
              <span>Weight Goal</span>
              <strong>{formatWeight(weightProgress.goal_weight_kg)} kg</strong>
            </div>
          )}
        </div>

        {loading ? (
          <p className="progress-empty">Loading weight history...</p>
        ) : chartData.length === 0 ? (
          <div className="progress-empty">
            <p>No weight entries yet.</p>
            <span>Record your first measurement below to start tracking your trend.</span>
          </div>
        ) : (
          <div className="progress-chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 12, right: 20, left: 4, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="recorded_date"
                  tickFormatter={(value) => formatDate(value)}
                  minTickGap={24}
                  tick={{ fill: "#6b7280", fontSize: 12 }}
                />
                <YAxis
                  domain={["dataMin - 2", "dataMax + 2"]}
                  width={48}
                  tick={{ fill: "#6b7280", fontSize: 12 }}
                  tickFormatter={(value) => `${value}`}
                />
                <Tooltip
                  labelFormatter={(value) => formatDate(value, { year: "numeric" })}
                  formatter={(value) => [`${Number(value).toFixed(2)} kg`, "Weight"]}
                />
                <Line
                  type="monotone"
                  dataKey="weight_kg"
                  name="Weight"
                  stroke="#16a34a"
                  strokeWidth={3}
                  dot={{ r: 4, fill: "#16a34a" }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {weightProgress?.goal_weight_kg != null && weightPercentage != null && (
          <div className="progress-weight-goal-summary">
            <div className="progress-card-heading">
              <span>Progress toward weight goal</span>
              <strong>{Number(weightPercentage).toFixed(1)}%</strong>
            </div>
            <div
              className="progress-goal-track"
              role="progressbar"
              aria-label="Progress toward weight goal"
              aria-valuemin="0"
              aria-valuemax="100"
              aria-valuenow={weightProgressWidth}
            >
              <span style={{ width: `${weightProgressWidth}%` }} />
            </div>
          </div>
        )}
      </section>

      <section className="card progress-weight-form-card">
        <h2>Record Your Weight</h2>
        <p className="progress-section-description">
          Add a measurement to update your weight history and progress chart.
        </p>
        <form onSubmit={handleWeightSubmit}>
          <div className="progress-weight-form-grid">
            <div className="progress-form-group">
              <label htmlFor="weight-value">Weight (kg)</label>
              <input
                id="weight-value"
                type="number"
                min="0.01"
                max="999.99"
                step="0.01"
                placeholder="e.g. 75.5"
                value={weight}
                onChange={(event) => setWeight(event.target.value)}
                required
              />
            </div>
            <div className="progress-form-group">
              <label htmlFor="weight-date">Measurement Date</label>
              <input
                id="weight-date"
                type="date"
                value={recordedDate}
                onChange={(event) => setRecordedDate(event.target.value)}
                required
              />
            </div>
          </div>
          <div className="progress-form-actions">
            <button
              type="submit"
              className="progress-primary-button"
              disabled={saving}
            >
              {saving ? "Saving..." : "Save Weight"}
            </button>
          </div>
        </form>
      </section>

      <section className="card progress-history-card">
        <h2>Weight History</h2>
        {loading ? (
          <p className="progress-empty">Loading entries...</p>
        ) : history.length === 0 ? (
          <p className="progress-empty">Your weight entries will appear here.</p>
        ) : (
          <div className="progress-history-list">
            {[...history].reverse().map((entry) => (
              <div className="progress-history-item" key={entry.id}>
                <span>{formatDate(entry.recorded_date, { year: "numeric" })}</span>
                <strong>{formatWeight(entry.weight_kg)} kg</strong>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
