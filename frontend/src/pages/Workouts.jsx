
import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Workouts() {
  const [workouts, setWorkouts] = useState([]);
  const [activity, setActivity] = useState("");
  const [duration, setDuration] = useState("");
  const [date, setDate] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadWorkouts() {
    try {
      setError("");
      const data = await api.getWorkouts();
      setWorkouts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadWorkouts();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      setError("");

      await api.addWorkout({
        activity_type: activity,
        duration_minutes: Number(duration),
        workout_date: date
      });

      setActivity("");
      setDuration("");
      setDate("");

      await loadWorkouts();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    try {
      setError("");
      await api.deleteWorkout(id);
      await loadWorkouts();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h1>Workout Tracker</h1>

      <section className="card">
        <h2>Log a Workout</h2>

        <form onSubmit={handleSubmit}>
          <input
            placeholder="Activity type"
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
            required
          />

          <input
            type="number"
            placeholder="Duration (minutes)"
            min="1"
            step="1"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            required
          />

          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />

          <button type="submit">Save Workout</button>
        </form>
      </section>

      {error && <p role="alert">{error}</p>}

      <section className="card">
        <h2>Workout History</h2>

        {loading ? (
          <p>Loading workouts...</p>
        ) : workouts.length === 0 ? (
          <p>No workouts recorded yet.</p>
        ) : (
          <ul>
            {workouts.map((workout) => (
              <li key={workout.id}>
                {workout.activity_type} —{" "}
                {workout.duration_minutes} minutes —{" "}
                {workout.workout_date}

                <button
                  onClick={() => handleDelete(workout.id)}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
