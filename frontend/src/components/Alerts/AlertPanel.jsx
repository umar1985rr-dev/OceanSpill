import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonRows } from "../ui/Skeleton";
import { severityTone } from "../ui/tone";
import { IconAlertTriangle } from "../ui/icons";

function AlertPanel() {
  const fetcher = useCallback(
    () => api.get("/alerts/history").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const alerts = (data?.alerts ?? []).slice(-5).reverse();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Marine Alert Center</CardTitle>
        <IconAlertTriangle className="text-muted" />
      </CardHeader>
      <CardContent className="space-y-3">
        {loading && !data ? (
          <SkeletonRows rows={3} />
        ) : error && !data ? (
          <ErrorState message="Alert feed is unavailable." />
        ) : alerts.length === 0 ? (
          <EmptyState title="No alerts dispatched yet" />
        ) : (
          alerts.map((alert, i) => (
            <div key={i} className="rounded-lg bg-slate-50 p-4">
              <div className="flex items-center justify-between gap-2">
                <Badge variant={severityTone(alert.severity)}>
                  {alert.severity}
                </Badge>
                <span className="text-xs text-muted">
                  {alert.sent_at
                    ? new Date(alert.sent_at).toLocaleTimeString()
                    : "—"}
                </span>
              </div>
              <div className="mt-2 text-sm font-semibold">{alert.title}</div>
              <div className="mt-0.5 text-sm text-muted">{alert.message}</div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}

export default AlertPanel;
