import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    // Generous timeout: the first /ais call parses a 241 MB CSV once on the
    // backend (tens of seconds); subsequent calls are cached and instant.
    timeout: 60000,
});

export default api;