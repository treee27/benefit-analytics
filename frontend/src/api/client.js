// VITE_API_BASE_URL is set in Vercel's environment variables for production.
// Locally, .env.local (not committed) sets it, or it falls back to localhost.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function fetchDashboardData(userId) {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/dashboard`);

  if (!response.ok) {
    throw new Error(`Dashboard request failed with status ${response.status}`);
  }

  return response.json();
}

export async function decideNudgeForTransaction(transactionPayload) {
  const response = await fetch(`${API_BASE_URL}/api/nudges/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(transactionPayload),
  });

  if (!response.ok) {
    throw new Error(`Nudge decision request failed with status ${response.status}`);
  }

  return response.json();
}