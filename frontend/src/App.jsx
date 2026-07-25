import Dashboard from "./pages/Dashboard.jsx";

// Hardcoded to user 1 for the hackathon demo — swap for real auth/user
// selection later if there's time.
const DEMO_USER_ID = 1;

export default function App() {
  return (
    <div className="app-shell">
      <Dashboard userId={DEMO_USER_ID} />
    </div>
  );
}
