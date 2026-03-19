const ACTIVITY_KEY = "docatrust_activity";
const LIMIT = 80;

export function addActivity(entry) {
  const current = getActivities();
  const next = [
    {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      at: new Date().toISOString(),
      ...entry,
    },
    ...current,
  ].slice(0, LIMIT);
  localStorage.setItem(ACTIVITY_KEY, JSON.stringify(next));
}

export function getActivities() {
  try {
    const raw = localStorage.getItem(ACTIVITY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}
