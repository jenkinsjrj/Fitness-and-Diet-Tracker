
async function request(endpoint, options = {}) {
  const response = await fetch(endpoint, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      error.error || `Request failed: ${response.status}`
    );
  }

  if (response.status === 204) return null;

  return response.json();
}

const jsonOptions = (method, data) => ({
  method,
  body: JSON.stringify(data),
});

export const api = {
  // Workouts
  getWorkouts: () => request("/api/workouts"),

  addWorkout: (data) =>
    request("/api/workouts", jsonOptions("POST", data)),

  deleteWorkout: (id) =>
    request(`/api/workouts/${id}`, { method: "DELETE" }),

  // Progress
  getWeights: () => request("/api/weights"),

  addWeight: (data) =>
    request("/api/weights", jsonOptions("POST", data)),

  getProgress: (weekStart) =>
    request(
      weekStart
        ? `/api/progress?week_start=${encodeURIComponent(weekStart)}`
        : "/api/progress"
    ),

  // Nutrition
  getFoods: () => request("/api/foods"),

  getMeals: (date) =>
    request(`/api/meals?date=${encodeURIComponent(date)}`),

  addMeal: (data) =>
    request("/api/meals", jsonOptions("POST", data)),

  deleteMeal: (id) =>
    request(`/api/meals/${id}`, { method: "DELETE" }),

  getNutrition: (date) =>
    request(`/api/nutrition?date=${encodeURIComponent(date)}`),

  getRecommendations: (date) =>
    request(`/api/recommendations?date=${encodeURIComponent(date)}`),

  // Reminders
  getReminders: () => request("/api/reminders"),

  addReminder: (data) =>
    request("/api/reminders", jsonOptions("POST", data)),

  updateReminder: (id, data) =>
    request(
      `/api/reminders/${id}`,
      jsonOptions("PATCH", data)
    ),

  deleteReminder: (id) =>
    request(`/api/reminders/${id}`, { method: "DELETE" }),
};
