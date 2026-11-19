
import { useEffect, useState } from "react";
import { api } from "../services/api";
import "./Calendar.css";

// Convert UTC timestamps to the user's local date/time.
function toLocalDateTime(value) {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "";

  const offset = date.getTimezoneOffset() * 60000;

  return new Date(date.getTime() - offset)
    .toISOString()
    .slice(0, 16);
}

function formatDateTime(value) {
  if (!value) return "No date";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Invalid date";
  }

  return date.toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  });
}

export default function Calendar() {
  const [reminders, setReminders] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");

  const [editingId, setEditingId] = useState(null);
  const [filter, setFilter] = useState("upcoming");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Retrieve reminders from the backend.
  async function loadReminders() {
    try {
      setError("");

      const data = await api.getReminders();

      setReminders(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReminders();
  }, []);

  function resetForm() {
    setTitle("");
    setDescription("");
    setScheduledAt("");
    setEditingId(null);
  }

  // Create a reminder or save changes to an existing one.
  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!title.trim()) {
      setError("Please enter a reminder title.");
      return;
    }

    if (title.trim().length > 150) {
      setError("Title cannot exceed 150 characters.");
      return;
    }

    if (!scheduledAt) {
      setError("Please select a date and time.");
      return;
    }

    const date = new Date(scheduledAt);

    if (Number.isNaN(date.getTime())) {
      setError("Please enter a valid date and time.");
      return;
    }

    const reminderData = {
      title: title.trim(),
      description: description.trim(),
      scheduled_at: date.toISOString()
    };

    try {
      setSaving(true);

      if (editingId !== null) {
        await api.updateReminder(
          editingId,
          reminderData
        );

        setSuccess("Reminder updated successfully.");
      } else {
        await api.addReminder(reminderData);

        setSuccess("Reminder created successfully.");
      }

      resetForm();
      await loadReminders();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  // Load an existing reminder into the form.
  function handleEdit(reminder) {
    setTitle(reminder.title);
    setDescription(reminder.description || "");
    setScheduledAt(
      toLocalDateTime(reminder.scheduled_at)
    );

    setEditingId(reminder.id);

    setError("");
    setSuccess("");

    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  }

  // Mark a reminder as completed or incomplete.
  async function handleToggleComplete(reminder) {
    setError("");
    setSuccess("");
    setBusyId(reminder.id);

    try {
      await api.updateReminder(reminder.id, {
        completed: !reminder.completed
      });

      setSuccess(
        reminder.completed
          ? "Reminder marked as incomplete."
          : "Reminder marked as completed."
      );

      await loadReminders();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  // Delete a reminder.
  async function handleDelete(reminder) {
    const confirmed = window.confirm(
      `Delete "${reminder.title}"?`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");
    setBusyId(reminder.id);

    try {
      await api.deleteReminder(reminder.id);

      if (editingId === reminder.id) {
        resetForm();
      }

      setSuccess("Reminder deleted successfully.");

      await loadReminders();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  const now = Date.now();

  // Sort reminders by scheduled date.
  const sortedReminders = [...reminders].sort(
    (a, b) =>
      new Date(a.scheduled_at).getTime() -
      new Date(b.scheduled_at).getTime()
  );

  const upcomingReminders = sortedReminders.filter(
    (reminder) =>
      !reminder.completed &&
      new Date(reminder.scheduled_at).getTime() >= now
  );

  const pastReminders = sortedReminders.filter(
    (reminder) =>
      !reminder.completed &&
      new Date(reminder.scheduled_at).getTime() < now
  );

  const completedReminders = sortedReminders.filter(
    (reminder) => reminder.completed
  );

  let displayedReminders = sortedReminders;

  if (filter === "upcoming") {
    displayedReminders = upcomingReminders;
  } else if (filter === "past") {
    displayedReminders = pastReminders;
  } else if (filter === "completed") {
    displayedReminders = completedReminders;
  }

  return (
    <div className="calendar-page">
      <div className="calendar-header">
        <h1>Calendar & Reminders</h1>
        <p>
          Schedule workouts, meals, and other fitness
          activities to stay on track with your goals.
        </p>
      </div>

      {/* Reminder summary */}
      <div className="reminder-stats">
        <div className="reminder-stat-card">
          <span>Upcoming</span>
          <strong>{upcomingReminders.length}</strong>
        </div>

        <div className="reminder-stat-card">
          <span>Past Due</span>
          <strong>{pastReminders.length}</strong>
        </div>

        <div className="reminder-stat-card">
          <span>Completed</span>
          <strong>{completedReminders.length}</strong>
        </div>
      </div>

      {error && (
        <div className="reminder-error" role="alert">
          {error}
        </div>
      )}

      {success && (
        <div className="reminder-success" role="status">
          {success}
        </div>
      )}

      {/* Create / Edit Reminder */}
      <section className="card reminder-form-card">
        <h2>
          {editingId !== null
            ? "Edit Reminder"
            : "Create Reminder"}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="reminder-form-group">
            <label htmlFor="reminder-title">
              Reminder Title
            </label>

            <input
              id="reminder-title"
              type="text"
              placeholder="e.g. Go to the gym"
              value={title}
              onChange={(event) =>
                setTitle(event.target.value)
              }
              maxLength={150}
              required
            />
          </div>

          <div className="reminder-form-group">
            <label htmlFor="reminder-description">
              Description (Optional)
            </label>

            <textarea
              id="reminder-description"
              placeholder="Add details about your reminder..."
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              rows={3}
            />
          </div>

          <div className="reminder-form-group">
            <label htmlFor="reminder-date">
              Date & Time
            </label>

            <input
              id="reminder-date"
              type="datetime-local"
              value={scheduledAt}
              onChange={(event) =>
                setScheduledAt(event.target.value)
              }
              required
            />
          </div>

          <div className="reminder-form-actions">
            <button
              type="submit"
              className="reminder-primary-button"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingId !== null
                  ? "Save Changes"
                  : "Create Reminder"}
            </button>

            {editingId !== null && (
              <button
                type="button"
                className="reminder-secondary-button"
                onClick={resetForm}
                disabled={saving}
              >
                Cancel Editing
              </button>
            )}
          </div>
        </form>
      </section>

      {/* Reminder list */}
      <section className="card reminder-list-card">
        <div className="reminder-list-header">
          <h2>My Reminders</h2>

          <button
            type="button"
            className="reminder-secondary-button"
            onClick={loadReminders}
            disabled={loading}
          >
            Refresh
          </button>
        </div>

        <div className="reminder-filters">
          <button
            type="button"
            className={filter === "upcoming" ? "selected" : ""}
            onClick={() => setFilter("upcoming")}
          >
            Upcoming
          </button>

          <button
            type="button"
            className={filter === "past" ? "selected" : ""}
            onClick={() => setFilter("past")}
          >
            Past Due
          </button>

          <button
            type="button"
            className={filter === "completed" ? "selected" : ""}
            onClick={() => setFilter("completed")}
          >
            Completed
          </button>

          <button
            type="button"
            className={filter === "all" ? "selected" : ""}
            onClick={() => setFilter("all")}
          >
            All
          </button>
        </div>

        {loading ? (
          <p>Loading reminders...</p>
        ) : displayedReminders.length === 0 ? (
          <div className="reminder-empty">
            <p>No reminders found.</p>
            <span>
              Create a reminder or select another filter.
            </span>
          </div>
        ) : (
          <div className="reminder-items">
            {displayedReminders.map((reminder) => {
              const isPast =
                !reminder.completed &&
                new Date(reminder.scheduled_at).getTime() < now;

              return (
                <div
                  key={reminder.id}
                  className={
                    `reminder-item ${
                      reminder.completed ? "completed" : ""
                    }`
                  }
                >
                  <div className="reminder-item-content">
                    <div className="reminder-item-heading">
                      <h3>{reminder.title}</h3>

                      <span
                        className={
                          `reminder-status ${
                            reminder.completed
                              ? "status-completed"
                              : isPast
                                ? "status-past"
                                : "status-upcoming"
                          }`
                        }
                      >
                        {reminder.completed
                          ? "Completed"
                          : isPast
                            ? "Past Due"
                            : "Upcoming"}
                      </span>
                    </div>

                    {reminder.description && (
                      <p className="reminder-description">
                        {reminder.description}
                      </p>
                    )}

                    <p className="reminder-date">
                      {formatDateTime(reminder.scheduled_at)}
                    </p>
                  </div>

                  <div className="reminder-item-actions">
                    <button
                      type="button"
                      className="reminder-complete-button"
                      onClick={() =>
                        handleToggleComplete(reminder)
                      }
                      disabled={busyId !== null}
                    >
                      {reminder.completed
                        ? "Mark Incomplete"
                        : "Complete"}
                    </button>

                    <button
                      type="button"
                      className="reminder-edit-button"
                      onClick={() => handleEdit(reminder)}
                      disabled={busyId !== null}
                    >
                      Edit
                    </button>

                    <button
                      type="button"
                      className="reminder-delete-button"
                      onClick={() => handleDelete(reminder)}
                      disabled={busyId !== null}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      <p className="reminder-note">
        Reminders are saved to your account's database.
        This version does not send automatic notifications
        or support recurring reminders.
      </p>
    </div>
  );
}
