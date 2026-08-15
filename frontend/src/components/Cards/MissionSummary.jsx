import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import { SkeletonRows } from "../ui/Skeleton";
import ErrorState from "../ui/ErrorState";
import { Field, FieldGrid } from "../ui/Field";
import { IconActivity } from "../ui/icons";

function MissionSummary() {
  const fetcher = useCallback(
    () => api.get("/monitoring/status").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const last = data?.last_detection;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mission Summary</CardTitle>
        <IconActivity className="text-muted" />
      </CardHeader>
      <CardContent>
        {loading && !data ? (
          <SkeletonRows rows={6} />
        ) : error && !data ? (
          <ErrorState message="Mission status is unavailable." />
        ) : (
          <FieldGrid className="grid-cols-1">
            <Field label="Incident ID" value={last?.id ?? "—"} />
            <Field
              label="Detection Time"
              value={last ? new Date(last.detected_at).toLocaleString() : "—"}
            />
            <Field
              label="Spill Status"
              value={
                last ? (
                  <span className="font-semibold text-danger">ACTIVE</span>
                ) : (
                  "SCANNING"
                )
              }
            />
            <Field label="AI Model" value="U-Net ResNet34" />
            <Field label="Satellite" value={data?.feed?.source ?? "—"} />
            <Field
              label="Confidence"
              value={last ? `${last.confidence}%` : "—"}
            />
            <Field
              label="Region"
              value={
                last ? `${last.latitude}, ${last.longitude}` : "—"
              }
              mono
            />
            <Field
              label="Last Updated"
              value={
                data?.last_checked_at
                  ? new Date(data.last_checked_at).toLocaleTimeString()
                  : "—"
              }
            />
          </FieldGrid>
        )}
      </CardContent>
    </Card>
  );
}

export default MissionSummary;
