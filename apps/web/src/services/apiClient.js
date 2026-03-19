import { getAuthToken } from "../lib/auth";

export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:4000";
export const PY_BASE = import.meta.env.VITE_PYTHON_API_URL || "http://localhost:8000";

async function parseJson(res) {
  return res.json().catch(() => ({}));
}

export async function apiRequest(path, options = {}) {
  const token = getAuthToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await parseJson(res);
  if (!res.ok) throw new Error(data.message || data.detail || res.statusText);
  return data;
}

export async function pyRequest(path, options = {}) {
  const res = await fetch(`${PY_BASE}${path}`, options);
  const data = await parseJson(res);
  if (!res.ok) throw new Error(data.message || data.detail || res.statusText);
  return data;
}

export async function apiFormRequest(path, formData) {
  const token = getAuthToken();
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  // Ne pas forcer Content-Type : le browser gère le boundary multipart automatiquement

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });
  const data = await parseJson(res);
  if (!res.ok) throw new Error(data.message || data.detail || res.statusText);
  return data;
}
