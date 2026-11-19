import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import "./Workouts.css";

function getLocalDateString(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getLocalWeekStartString() {
  const monday = new Date();
  monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7));
  return getLocalDateString(monday);
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(`${value}T12:00:00`);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString([], {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
}

export default function Workouts() {
  const [workouts, setWorkouts] = useState([]);
  const [weeklyProgress, setWeeklyProgress] = useState(null);
  const [activity, setActivity] = useState("");
  const [duration, setDuration] = useState("");
  const [date, setDate] = useState(getLocalDateString);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);

  const loadData = useCallback(async () => {
    setError("");
    const [workoutResult, progressResult] = await Promise.allSettled([
      api.getWorkouts(),
      api.getProgress(getLocalWeekStartString()),
    ]);

    if (workoutResult.status === "fulfilled") {
      setWorkouts(Array.isArray(workoutResult.value) ? workoutResult.value : []);
    } else {
      setError(workoutResult.reason.message || "Unable to load workouts.");
    }

    if (progressResult.status === "fulfilled") {
      setWeeklyProgress(progressResult.value?.workouts ?? null);
    } else if (workoutResult.status === "fulfilled") {
      setError(
        `Workouts loaded, but weekly summary is unavailable: ${progressResult.reason.message}`
      );
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const sortedWorkouts = useMemo(
    () =>
      [...workouts].sort((a, b) => {
        const dateOrder = (b.workout_date || "").localeCompare(a.workout_date || "");
        return dateOrder || Number(b.id) - Number(a.id);
      }),
    [workouts]
  );

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const trimmedActivity = activity.trim();
    const minutes = Number(duration);

    if (!trimmedActivity) {
      setError("Please enter an activity type.");
      return;
    }
    if (trimmedActivity.length > 100) {
      setError("Activity type must be 100 characters or fewer.");
      return;
    }
    if (!Number.isInteger(minutes) || minutes <= 0) {
      setError("Workout duration must be a positive whole number of minutes.");
      return;
    }
    if (!date) {
      setError("Please select the workout date.");
      return;
    }

    try {
      setSaving(true);
      await api.addWorkout({
        activity_type: trimmedActivity,
        duration_minutes: minutes,
        workout_date: date,
      });
      setActivity("");
      setDuration("");
      setDate(getLocalDateString());
      setSuccess("Workout saved successfully.");
      await loadData();
    } catch (err) {
      setError(err.message || "Unable to save workout.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(workout) {
    const confirmed = window.confirm(
      `Delete your ${workout.activity_type} workout from ${formatDate(workout.workout_date)}?`
    );
    if (!confirmed) return;

    setError("");
    setSuccess("");
    setBusyId(workout.id);
    try {
      await api.deleteWorkout(workout.id);
      setSuccess("Workout deleted.");
      await loadData();
    } catch (err) {
      setError(err.message || "Unable to delete workout.");
    } finally {
      setBusyId(null);
    }
  }

  const count = weeklyProgress?.count ?? "—";
  const goal = weeklyProgress?.weekly_goal ?? "—";
  const percentage = Number(weeklyProgress?.goal_progress_percentage ?? 0);
  const progressWidth = Math.min(Math.max(percentage, 0), 100);

  return (
    <div className="workouts-page">
      <header className="workouts-header">
        <div>
          <h1>Workout Tracker</h1>
          <p>Log completed workouts and keep track of your weekly activity.</p>
        </div>
        <button
          type="button"
          className="workout-secondary-button"
          onClick={loadData}
          disabled={loading || saving || busyId !== null}
        >
          Refresh
        </button>
      </header>

      <section className="workout-stats-grid" aria-label="Weekly workout summary">
        <article className="workout-stat-card">
          <span>Workouts This Week</span>
          <strong>{count}<small> / {goal}</small></strong>
          <p>{weeklyProgress?.remaining ?? "—"} workouts remaining</p>
        </article>
        <article className="workout-stat-card">
          <span>Minutes This Week</span>
          <strong>{weeklyProgress?.total_minutes ?? "—"}<small> min</small></strong>
          <p>Total completed workout time</p>
        </article>
        <article className="workout-stat-card workout-stat-progress">
          <div className="workout-stat-topline">
            <span>Weekly Goal</span>
            <strong>{weeklyProgress ? `${percentage.toFixed(1)}%` : "—"}</strong>
          </div>
          <div
            className="workout-progress-track"
            role="progressbar"
            aria-label="Weekly workout goal progress"
            aria-valuemin="0"
            aria-valuemax="100"
            aria-valuenow={progressWidth}
          >
            <span style={{ width: `${progressWidth}%` }} />
          </div>
          <p>
            {weeklyProgress?.goal_met
              ? "Weekly goal reached. Nice work!"
              : "Progress toward your weekly workout target"}
          </p>
        </article>
      </section>

      {error && <div className="workout-error" role="alert">{error}</div>}
      {success && <div className="workout-success" role="status">{success}</div>}

      <section className="card workout-form-card">
        <h2>Log a Workout</h2>
        <p className="workout-section-description">
          Add a completed activity to your workout history.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="workout-form-grid">
            <div className="workout-form-group">
              <label htmlFor="workout-activity">Activity Type</label>
              <input
                id="workout-activity"
                type="text"
                list="workout-activity-options"
                placeholder="e.g. Running, Weightlifting, Cycling"
                value={activity}
                onChange={(event) => setActivity(event.target.value)}
                maxLength={100}
                required
              />
              <datalist id="workout-activity-options">
                <option value="Running" />
                <option value="Weightlifting" />
                <option value="Cycling" />
                <option value="Walking" />
                <option value="Swimming" />
                <option value="Yoga" />
                <option value="Basketball" />
              </datalist>
            </div>

            <div className="workout-form-group">
              <label htmlFor="workout-duration">Duration (minutes)</label>
              <input
                id="workout-duration"
                type="number"
                placeholder="e.g. 45"
                min="1"
                step="1"
                value={duration}
                onChange={(event) => setDuration(event.target.value)}
                required
              />
            </div>

            <div className="workout-form-group">
              <label htmlFor="workout-date">Workout Date</label>
              <input
                id="workout-date"
                type="date"
                value={date}
                onChange={(event) => setDate(event.target.value)}
                required
              />
            </div>
          </div>

          <div className="workout-form-actions">
            <button
              type="submit"
              className="workout-primary-button"
              disabled={saving}
            >
              {saving ? "Saving..." : "Save Workout"}
            </button>
          </div>
        </form>
      </section>

      <section className="card workout-history-card">
        <div className="workout-history-header">
          <div>
            <h2>Workout History</h2>
            <p className="workout-section-description">
              {workouts.length} {workouts.length === 1 ? "workout" : "workouts"} recorded
            </p>
          </div>
        </div>

        {loading ? (
          <p className="workout-empty">Loading workouts...</p>
        ) : sortedWorkouts.length === 0 ? (
          <div className="workout-empty">
            <p>No workouts recorded yet.</p>
            <span>Your saved workouts will appear here.</span>
          </div>
        ) : (
          <div className="workout-history-list">
            {sortedWorkouts.map((workout) => (
              <article className="workout-history-item" key={workout.id}>
                <div className="workout-history-main">
                  <div className="workout-activity-mark" aria-hidden="true">
                    {workout.activity_type?.slice(0, 1).toUpperCase() || "W"}
                  </div>
                  <div className="workout-history-details">
                    <h3>{workout.activity_type}</h3>
                    <p>{formatDate(workout.workout_date)}</p>
                  </div>
                </div>
                <div className="workout-history-meta">
                  <strong>{workout.duration_minutes} min</strong>
                  <button
                    type="button"
                    className="workout-delete-button"
                    onClick={() => handleDelete(workout)}
                    disabled={busyId !== null || saving}
                    aria-label={`Delete ${workout.activity_type} workout from ${formatDate(workout.workout_date)}`}
                  >
                    {busyId === workout.id ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
