import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonRows } from "../ui/Skeleton";
import { Field, FieldGrid } from "../ui/Field";
import { IconShip } from "../ui/icons";

function AISPanel() {
  const fetcher = useCallback(
    () => api.get("/ais/suspect-vessels").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const vessels = (data?.vessels ?? []).slice(0, 2).map((v) => ({
    name: v.VesselName ?? v.MMSI ?? "Unknown",
    mmsi: v.MMSI ?? "—",
    speed: `${v.SOG ?? "—"} knots`,
    heading: `${v.COG ?? "—"}°`,
    type: v.VesselType ?? "—",
    high: (v.SuspectScore ?? 0) >= 70,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Suspected Vessel Intelligence</CardTitle>
        <IconShip className="text-muted" />
      </CardHeader>
      <CardContent className="space-y-4">
        {loading && !data ? (
          <SkeletonRows rows={3} />
        ) : error && !data ? (
          <ErrorState message="Vessel intelligence is unavailable." />
        ) : vessels.length === 0 ? (
          <EmptyState title="No vessels in range" />
        ) : (
          vessels.map((v, i) => (
            <div key={i} className="rounded-lg border border-border p-4">
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold">{v.name}</span>
                <Badge variant={v.high ? "danger" : "warning"}>
                  {v.high ? "High" : "Medium"} suspect
                </Badge>
              </div>
              <FieldGrid className="mt-3">
                <Field label="MMSI" value={v.mmsi} mono />
                <Field label="Speed" value={v.speed} />
                <Field label="Heading" value={v.heading} />
                <Field label="Type" value={v.type} />
              </FieldGrid>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}

export default AISPanel;
