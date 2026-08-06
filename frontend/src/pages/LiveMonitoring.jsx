import { useCallback } from "react";
import api from "../services/api";
import { POLL_INTERVAL } from "../config";
import { usePolling } from "../hooks/usePolling";
import PageHeader from "../components/ui/PageHeader";
import Stat from "../components/ui/Stat";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "../components/ui/Card";
import EmptyState from "../components/ui/EmptyState";
import ErrorState from "../components/ui/ErrorState";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeadCell,
  TableCell,
} from "../components/ui/Table";
import { Field, FieldGrid } from "../components/ui/Field";
import { riskTone, severityTone } from "../components/ui/tone";
import {
  IconRadio,
  IconActivity,
  IconDroplet,
  IconAlertTriangle,
} from "../components/ui/icons";

function LiveMonitoring() {
  const statusFetcher = useCallback(
    () => api.get("/monitoring/status").then((r) => r.data),
    [],
  );
  const historyFetcher = useCallback(
    () => api.get("/monitoring/history").then((r) => r.data),
    [],
  );
  const alertsFetcher = useCallback(
    () => api.get("/alerts/history").then((r) => r.data),
    [],
  );

  const { data: status, error: statusError } = usePolling(
    statusFetcher,
    POLL_INTERVAL,
  );
  const { data: history, error: historyError } = usePolling(
    historyFetcher,
    POLL_INTERVAL,
  );
  const { data: alerts } = usePolling(alertsFetcher, POLL_INTERVAL);

  const toggleMonitoring = async () => {
    const action = status?.is_running ? "stop" : "start";
    try {
      await api.get(`/monitoring/${action}`);
    } catch {
      /* ignore */
    }
  };

  const incidents = history?.incidents ?? [];
  const alertList = alerts?.alerts ?? [];
  const latest = status?.last_detection ?? null;
  const feed = status?.feed ?? {};
  const running = status?.is_running === true;

  return (
    <div>
      <PageHeader
        title="Live Satellite Monitoring"
        description="The detection loop polls the satellite feed and triggers the full response pipeline when a spill is found"
        badge={<Badge variant={running ? "success" : "danger"} dot>{running ? "Running" : "Stopped"}</Badge>}
      >
        <Button
          variant={running ? "danger" : "primary"}
          onClick={toggleMonitoring}
        >
          {running ? "Stop Monitoring" : "Start Monitoring"}
        </Button>
        <Button variant="outline" href="/reports">
          View Incident Reports
        </Button>
      </PageHeader>

      {statusError && (
        <div className="mb-6">
          <ErrorState message="Cannot reach the monitoring service." />
        </div>
      )}

      {/* Status strip */}
      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat
          label="Status"
          value={running ? "Running" : "Stopped"}
          tone={running ? "success" : "danger"}
          icon={<IconRadio />}
        />
        <Stat
          label="Frames Served"
          value={feed.frames_served ?? 0}
          tone="info"
          icon={<IconActivity />}
        />
        <Stat
          label="Interval"
          value={`${status?.interval_seconds ?? "-"}s`}
          tone="default"
          icon={<IconDroplet />}
        />
        <Stat
          label="Incidents"
          value={history?.count ?? 0}
          tone={running ? "default" : "default"}
          icon={<IconAlertTriangle />}
        />
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Latest detection */}
        <Card>
          <CardHeader>
            <CardTitle>Latest Detection</CardTitle>
            {latest && <Badge variant={riskTone(latest.risk_level)}>{latest.risk_level}</Badge>}
          </CardHeader>
          <CardContent>
            {!latest ? (
              <EmptyState
                title="No detection yet"
                description="Monitoring in progress — results will appear here."
              />
            ) : (
              <FieldGrid className="grid-cols-1">
                <Field label="Incident" value={latest.id} />
                <Field
                  label="Risk"
                  value={
                    <Badge variant={riskTone(latest.risk_level)}>
                      {latest.risk_level}
                    </Badge>
                  }
                />
                <Field label="Spill Area" value={`${latest.spill_area_km2} km²`} />
                <Field label="Confidence" value={`${latest.confidence}%`} />
                <Field
                  label="Location"
                  value={`${latest.latitude}, ${latest.longitude}`}
                  mono
                />
                <Field
                  label="Suspect Vessel"
                  value={latest.suspect_vessel?.ShipName ?? "—"}
                />
                <Field
                  label="Detected At"
                  value={new Date(latest.detected_at).toLocaleTimeString()}
                />
              </FieldGrid>
            )}
          </CardContent>
        </Card>

        {/* Recommended response */}
        <Card>
          <CardHeader>
            <CardTitle>Recommended Response</CardTitle>
            {latest?.cleanup && (
              <Badge
                variant={
                  String(latest.cleanup.Priority ?? latest.cleanup.priority ?? "")
                    .toLowerCase() === "high"
                    ? "danger"
                    : "info"
                }
              >
                {latest.cleanup.Priority ?? latest.cleanup.priority}
              </Badge>
            )}
          </CardHeader>
          <CardContent>
            {!latest?.cleanup ? (
              <EmptyState title="Waiting for a detection" />
            ) : (
              <div className="space-y-4">
                <FieldGrid className="grid-cols-1">
                  <Field
                    label="Equipment"
                    value={(latest.cleanup.Equipment ?? []).join(", ")}
                  />
                </FieldGrid>
                <div>
                  <div className="mb-2 text-xs font-medium uppercase tracking-wide text-muted">
                    Recommendations
                  </div>
                  <ul className="list-inside list-disc space-y-1.5 text-sm">
                    {(latest.cleanup.Recommendations ?? []).map((rec, i) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Incident history */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Incident History</CardTitle>
        </CardHeader>
        <CardContent>
          {historyError ? (
            <ErrorState message="Incident history is unavailable." />
          ) : incidents.length === 0 ? (
            <EmptyState title="No incidents recorded yet" />
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeadCell>Incident ID</TableHeadCell>
                  <TableHeadCell>Time</TableHeadCell>
                  <TableHeadCell>Spill %</TableHeadCell>
                  <TableHeadCell>Area (km²)</TableHeadCell>
                  <TableHeadCell>Risk</TableHeadCell>
                  <TableHeadCell>Suspect</TableHeadCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {incidents
                  .slice(-10)
                  .reverse()
                  .map((inc) => (
                    <TableRow key={inc.id}>
                      <TableCell className="tabular-nums">{inc.id}</TableCell>
                      <TableCell>
                        {new Date(inc.detected_at).toLocaleTimeString()}
                      </TableCell>
                      <TableCell className="tabular-nums">
                        {inc.spill_percentage}
                      </TableCell>
                      <TableCell className="tabular-nums">
                        {inc.spill_area_km2}
                      </TableCell>
                      <TableCell>
                        <Badge variant={riskTone(inc.risk_level)}>
                          {inc.risk_level}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {inc.suspect_vessel?.ShipName ?? "—"}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Notifications</CardTitle>
        </CardHeader>
        <CardContent>
          {alertList.length === 0 ? (
            <EmptyState title="No alerts dispatched" />
          ) : (
            <div className="space-y-2">
              {alertList.slice(-8).reverse().map((alert, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between gap-3 rounded-lg bg-slate-50 px-4 py-3 text-sm"
                >
                  <div className="flex items-center gap-3">
                    <Badge variant={severityTone(alert.severity)}>
                      {alert.severity}
                    </Badge>
                    <span className="font-medium">{alert.title}</span>
                  </div>
                  <span className="shrink-0 text-xs text-muted">
                    {new Date(alert.sent_at).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default LiveMonitoring;
