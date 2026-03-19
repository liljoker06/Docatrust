const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

function getToken() {
  return localStorage.getItem("admin_token");
}

function setToken(token) {
  localStorage.setItem("admin_token", token);
}

function removeToken() {
  localStorage.removeItem("admin_token");
}

async function request(method, path, body = null) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.message || "Erreur serveur");
  return data;
}

export const api = {
  // Auth
  login: (email, password) =>
    request("POST", "/api/users/login", { email, password }),
  me: () => request("GET", "/api/users/me"),
  setToken,
  removeToken,
  getToken,

  // Stats
  getStats: () => request("GET", "/api/admin/stats"),

  // Users
  listUsers: () => request("GET", "/api/admin/users"),
  updateUserRole: (id, role) =>
    request("PATCH", `/api/admin/users/${id}/role`, { role }),
  disableUser: (id) => request("PATCH", `/api/admin/users/${id}/disable`),
  deleteUser: (id) => request("DELETE", `/api/admin/users/${id}`),

  // Documents
  listAllDocuments: () => request("GET", "/api/admin/documents"),
  getDocumentDetails: (id) => request("GET", `/api/admin/documents/${id}`),

  // Alerts
  listAlerts: () => request("GET", "/api/admin/alerts"),
  resolveAlert: (id) => request("PATCH", `/api/admin/alerts/${id}/resolve`),

  // Logs
  listLogs: () => request("GET", "/api/admin/logs"),
};
