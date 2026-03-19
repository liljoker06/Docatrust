import { apiRequest } from "./apiClient";

export async function loginApi(email, password) {
  return apiRequest("/api/users/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function registerApi(email, password) {
  return apiRequest("/api/users", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function meApi() {
  return apiRequest("/api/users/me", { method: "GET" });
}
