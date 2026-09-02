import { useEffect, useState } from "react";
import api from "../services/api";
import { usePolling } from "./usePolling";

export const TN_FALLBACK_LOCATION = { lat: 13.08, lon: 80.27 };

/**
 * Resolve the incident location with the same priority as the backend:
 * 1) Live detection (monitoring/status → last_detection)
 * 2) Configured incident (config → incident_latitude/longitude)
 * 3) Tamil Nadu fallback (13.08, 80.27)
 *
 * Returns { location: { lat, lon } | null, loading, error }
 */
export function useIncidentLocation() {
  const [configLocation, setConfigLocation] = useState(null);
  const [configLoading, setConfigLoading] = useState(true);
  const [configError, setConfigError] = useState(null);

  // Fetch /config once on mount (it's an explicit setting, effectively static)
  useEffect(() => {
    let cancelled = false;
    api.get("/config")
      .then((r) => {
        if (!cancelled) {
          const lat = r.data.incident_latitude;
          const lon = r.data.incident_longitude;
          if (lat != null && lon != null) {
            setConfigLocation({ lat: Number(lat), lon: Number(lon) });
          }
          setConfigLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setConfigError(err);
          setConfigLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, []);

  // Poll monitoring/status for live detection
  const fetcher = () => api.get("/monitoring/status").then((r) => r.data);
  const { data: status, loading: statusLoading, error: statusError } = usePolling(fetcher, 3000);

  const liveDetection = status?.last_detection;
  const hasLive = liveDetection && liveDetection.latitude != null && liveDetection.longitude != null;

  // Resolve: live > config > fallback
  const location = hasLive
    ? { lat: liveDetection.latitude, lon: liveDetection.longitude }
    : (configLocation ?? TN_FALLBACK_LOCATION);

  const loading = statusLoading || configLoading;
  const error = statusError || configError;

  return { location, loading, error, source: hasLive ? "live" : (configLocation ? "config" : "fallback") };
}