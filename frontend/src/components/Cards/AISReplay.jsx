import { useCallback, useState } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonRows } from "../ui/Skeleton";
import { Field, FieldGrid } from "../ui/Field";
import { IconRadio } from "../ui/icons";

function AISReplay() {
  const [time, setTime] = useState(75);

  const fetcher = useCallback(
    () => api.get("/ais/nearby-vessels").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const vessel = data?.vessels?.[0];

  return (
    <Card>
      <CardHeader>
        <CardTitle>AIS Vessel Tracking</CardTitle>
        <IconRadio className="text-muted" />
      </CardHeader>
      <CardContent>
        {loading && !data ? (
          <SkeletonRows rows={3} />
        ) : error && !data ? (
          <ErrorState message="Vessel track is unavailable." />
        ) : !vessel ? (
          <EmptyState
            title="No vessel track available"
            description="Replay is available when the live backend is online."
          />
        ) : (
          <>
            <div className="mb-4">
              <div className="text-xs font-medium uppercase tracking-wide text-muted">
                Selected Vessel
              </div>
              <div className="mt-1 text-lg font-bold text-primary">
                {vessel.VesselName ?? "—"}
              </div>
            </div>

            <input
              type="range"
              min="0"
              max="100"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              className="w-full accent-primary"
              aria-label="24-hour vessel track timeline"
            />
            <div className="mt-1 flex justify-between text-xs text-muted">
              <span>00:00</span>
              <span>{time}%</span>
              <span>24:00</span>
            </div>

            <FieldGrid className="mt-5">
              <Field
                label="Position"
                value={`${vessel?.LAT ?? "—"}, ${vessel?.LON ?? "—"}`}
                mono
              />
              <Field label="MMSI" value={vessel?.MMSI ?? "—"} mono />
              <Field label="Speed" value={`${vessel?.SOG ?? "—"} knots`} />
              <Field label="Heading" value={`${vessel?.COG ?? "—"}°`} />
            </FieldGrid>

            <p className="mt-5 border-t border-border pt-4 text-xs text-muted">
              Timeline playback is available when a full vessel track is loaded
              from the live backend.
            </p>
          </>
        )}
      </CardContent>
    </Card>
  );
}

export default AISReplay;
