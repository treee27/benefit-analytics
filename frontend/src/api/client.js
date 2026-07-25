const API_BASE_URL = "http://localhost:8000";

export async function fetchDashboardData(userId) {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/dashboard`);

  if (!response.ok) {
    throw new Error(`Dashboard request failed with status ${response.status}`);
  }

  return response.json();
}
