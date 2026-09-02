// The backend serves the built SPA AND the API from one process, so by
// default we use relative (same-origin) URLs. This keeps the app immune to
// hostname/port mismatches (localhost vs 127.0.0.1, IPv4 vs IPv6, dev vs prod
// port) that otherwise make a healthy backend look "offline" via CORS.
// Set VITE_API_URL when the API genuinely lives on another host.
export const API_URL = import.meta.env.VITE_API_URL || "";
// API endpoints all live under the /api prefix (backend/main.py); API_BASE
// is used by both the axios instance and any manually-built URLs.
export const API_BASE = `${API_URL}/api`;
export const POLL_INTERVAL = 3000;
// How often the backend event watcher polls /monitoring/status for a new
// detection or a backend (re)start. When either is seen, every panel refreshes
// immediately.
export const EVENT_POLL_INTERVAL = 2000;
