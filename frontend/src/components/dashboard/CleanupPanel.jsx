import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonCard } from "../ui/Skeleton";

function CleanupPanel() {
  const fetcher = useCallback(
    () => api.get("/cleanup/recommend").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  if (loading && !data) return <SkeletonCard />;
  if (error && !data)
    return (
      <Card>
        <CardContent>
          <ErrorState message="Response recommendation is unavailable." />
        </CardContent>
      </Card>
    );

  const high = String(data?.Priority ?? "").toLowerCase() === "high";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Incident Response Recommendation</CardTitle>
        <Badge variant={high ? "danger" : "info"}>
          {data?.Priority ?? "—"} Priority
        </Badge>
      </CardHeader>
      <CardContent>
        {!data ? (
          <EmptyState title="No response recommendation yet" />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded-lg border-l-4 border-primary bg-slate-50 p-4">
              <h3 className="mb-3 text-sm font-semibold">
                Recommended Equipment
              </h3>
              <ul className="space-y-1.5 text-sm text-foreground">
                {(data.Equipment ?? []).map((item, i) => (
                  <li key={i} className="flex gap-2">
                    <span aria-hidden="true">✔</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-lg border-l-4 border-primary bg-slate-50 p-4">
              <h3 className="mb-3 text-sm font-semibold">
                Recommended Actions
              </h3>
              <ul className="space-y-1.5 text-sm text-foreground">
                {(data.Recommendations ?? []).map((item, i) => (
                  <li key={i} className="flex gap-2">
                    <span aria-hidden="true">✔</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default CleanupPanel;
