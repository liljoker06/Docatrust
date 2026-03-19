const AUTH_KEY = "docatrust_auth";

export function getAuthSession() {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  return Boolean(getAuthSession()?.token);
}

export function setAuthSession(payload) {
  localStorage.setItem(
    AUTH_KEY,
    JSON.stringify({
      token: payload?.token || "local-session-token",
      email: payload?.email || payload?.user?.email || "",
      name: payload?.name || payload?.user?.name || "",
      role: payload?.role || payload?.user?.role || "USER",
      userId: payload?.userId || payload?.user?.id || null,
      createdAt: new Date().toISOString(),
    })
  );
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_KEY);
}

export function getAuthToken() {
  return getAuthSession()?.token || "";
}
