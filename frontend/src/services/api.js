import axios from "axios";
import { API_BASE } from "../config";

const api = axios.create({
    // Relative by default so the page talks to the very server that served
    // it — no CORS, no host/port/IPv6 mismatches. See config.js.
    baseURL: API_BASE,
    // Generous timeout: the first /ais call parses a large CSV once on the
    // backend (tens of seconds); subsequent calls are cached and instant.
    timeout: 60000,
});

// Inject access token into every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// On 401: clear tokens and redirect to login — NEVER on auth endpoints
// (login returns 401 for wrong credentials; we must let the form show the error)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const url = error.config?.url || "";
        const isAuthCall = url.includes("/auth/login") ||
                           url.includes("/auth/refresh") ||
                           url.includes("/auth/register");
        if (error.response?.status === 401 && !isAuthCall) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            localStorage.removeItem("user");
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

export default api;
