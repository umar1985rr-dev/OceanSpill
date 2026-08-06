import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonRows } from "../ui/Skeleton";
import { riskTone } from "../ui/tone";
import { Field, FieldGrid } from "../ui/Field";

const fmt = (value) =>
  value != null ? `$${Number(value).toLocaleString()}` : "—";

function ImpactPanel() {
  const fetcher = useCallback(
    () => api.get("/impact/dashboard").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const riskLevel = data?.["Risk Level"] ?? "—";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Environmental & Economic Impact</CardTitle>
        <Badge variant={riskTone(riskLevel)}>{riskLevel}</Badge>
      </CardHeader>
      <CardContent>
        {loading && !data ? (
          <SkeletonRows rows={6} />
        ) : error && !data ? (
          <ErrorState message="Impact assessment is unavailable." />
        ) : !data ? (
          <EmptyState title="No impact assessment yet" />
        ) : (
          <div className="space-y-4">
            <FieldGrid className="grid-cols-1">
              <Field label="Risk Score" value={data["Risk Score"] ?? "—"} />
              <Field
                label="Response Priority"
                value={data["Response Priority"] ?? "—"}
              />
              <Field
                label="Nearest Coastline"
                value={
                  data["Nearest Coastline"] != null
                    ? `${data["Nearest Coastline"]} km`
                    : "—"
                }
              />
              <Field
                label="Protected Area"
                value={
                  data["Nearest Protected Area"] != null
                    ? `${data["Nearest Protected Area"]} km`
                    : "—"
                }
              />
              <Field label="Cleanup Cost" value={fmt(data["Cleanup Cost"])} />
              <Field label="Economic Loss" value={fmt(data["Economic Loss"])} />
            </FieldGrid>

            {data?.Recommendations?.length > 0 && (
              <div className="rounded-md border-l-4 border-primary bg-slate-50 p-3">
                <div className="mb-2 text-sm font-semibold">
                  Recommended Actions
                </div>
                <ul className="list-inside list-disc space-y-1 text-sm text-foreground">
                  {data.Recommendations.slice(0, 4).map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default ImpactPanel;
