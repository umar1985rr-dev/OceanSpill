export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
export const POLL_INTERVAL = 3000;
// How often the backend event watcher polls /monitoring/status for a new
// detection or a backend (re)start. When either is seen, every panel refreshes
// immediately.
export const EVENT_POLL_INTERVAL = 2000;
