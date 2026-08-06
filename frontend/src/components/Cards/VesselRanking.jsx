import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonRows } from "../ui/Skeleton";
import { IconShip } from "../ui/icons";

function VesselRanking() {
  const fetcher = useCallback(
    () => api.get("/ais/suspect-vessels").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const topVessels = (data?.vessels ?? []).slice(0, 3);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Suspected Vessel Ranking</CardTitle>
        <IconShip className="text-muted" />
      </CardHeader>
      <CardContent className="space-y-3">
        {loading && !data ? (
          <SkeletonRows rows={3} />
        ) : error && !data ? (
          <ErrorState message="Vessel ranking is unavailable." />
        ) : topVessels.length === 0 ? (
          <EmptyState title="No suspect vessels found" />
        ) : (
          topVessels.map((ship, index) => (
            <div
              key={ship.MMSI ?? index}
              className="flex items-start justify-between gap-3 rounded-lg border border-border p-4"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold tabular-nums text-slate-600">
                    {index + 1}
                  </span>
                  <span className="truncate font-semibold">
                    {ship.VesselName ?? ship.MMSI ?? "Unknown"}
                  </span>
                </div>
                <div className="mt-1.5 space-y-0.5 text-xs text-muted">
                  <div>
                    📍 {ship.Distance_km ?? "—"} km from spill
                  </div>
                  <div>⚓ MMSI {ship.MMSI ?? "—"}</div>
                  <div>
                    🧭 {ship.SOG ?? "—"} knots · heading {ship.COG ?? "—"}°
                  </div>
                </div>
              </div>
              <Badge variant="danger" className="shrink-0">
                {ship.SuspectScore ?? "—"}%
              </Badge>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}

export default VesselRanking;
