import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonRows } from "../ui/Skeleton";
import { Field, FieldGrid } from "../ui/Field";
import { IconWifi } from "../ui/icons";

function WeatherPanel() {
  const fetcher = useCallback(
    () => api.get("/weather/current").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Marine Weather & Ocean Conditions</CardTitle>
        <IconWifi className="text-muted" />
      </CardHeader>
      <CardContent>
        {loading && !data ? (
          <SkeletonRows rows={3} />
        ) : error && !data ? (
          <ErrorState message="Weather feed is unavailable." />
        ) : !data ? (
          <EmptyState title="No weather data yet" />
        ) : (
          <>
            <FieldGrid>
              <Field label="Wind Speed" value={`${data.wind_speed_kmh} km/h`} />
              <Field
                label="Wind Direction"
                value={
                  data.wind_direction_deg != null
                    ? `${data.wind_direction_deg}°`
                    : "—"
                }
              />
              <Field label="Sea Current" value={`${data.current_speed} m/s`} />
              <Field
                label="Current Direction"
                value={
                  data.current_direction != null
                    ? `${data.current_direction}°`
                    : "—"
                }
              />
            </FieldGrid>

            <div className="mt-5 flex items-center justify-between border-t border-border pt-4 text-xs text-muted">
              <span>Open-Meteo · {data.latitude?.toFixed(2)}, {data.longitude?.toFixed(2)}</span>
              <span>Live (polled every 3s)</span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

export default WeatherPanel;
