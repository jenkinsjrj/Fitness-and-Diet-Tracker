
import {
  BrowserRouter,
  NavLink,
  Routes,
  Route
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Workouts from "./pages/Workouts";
import Progress from "./pages/Progress";
import Nutrition from "./pages/Nutrition";
import Recommendations from "./pages/Recommendations";
import Calendar from "./pages/Calendar";

import "./index.css";

const navigation = [
  { name: "Dashboard", path: "/" },
  { name: "Workouts", path: "/workouts" },
  { name: "Progress", path: "/progress" },
  { name: "Nutrition", path: "/nutrition" },
  { name: "Recommendations", path: "/recommendations" },
  { name: "Calendar", path: "/calendar" }
];

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <aside className="sidebar">
          <h2>FitTrack</h2>

          <nav>
            {navigation.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                className={({ isActive }) =>
                  isActive
                    ? "nav-link active"
                    : "nav-link"
                }
              >
                {item.name}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/workouts" element={<Workouts />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="/nutrition" element={<Nutrition />} />
            <Route
              path="/recommendations"
              element={<Recommendations />}
            />
            <Route path="/calendar" element={<Calendar />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
