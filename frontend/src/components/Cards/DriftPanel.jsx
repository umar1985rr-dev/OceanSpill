import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonRows } from "../ui/Skeleton";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeadCell,
  TableCell,
} from "../ui/Table";

function DriftPanel() {
  const fetcher = useCallback(
    () => api.get("/drift/predict").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const predictions = data?.predictions ?? [];
  const hours = predictions.length;
  const lastPoint = predictions[predictions.length - 1];
  const firstPoint = predictions[0];

  const totalKm =
    firstPoint && lastPoint
      ? (
          Math.sqrt(
            (lastPoint.latitude - firstPoint.latitude) ** 2 +
              (lastPoint.longitude - firstPoint.longitude) ** 2,
          ) * 111
        ).toFixed(1)
      : "—";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Oil Spill Drift Forecast</CardTitle>
        <Badge variant="info">{hours} HOURS</Badge>
      </CardHeader>
      <CardContent>
        {loading && !data ? (
          <SkeletonRows rows={3} />
        ) : error && !data ? (
          <ErrorState message="Drift forecast is unavailable." />
        ) : predictions.length === 0 ? (
          <EmptyState title="No drift forecast available" />
        ) : (
          <div className="space-y-4">
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeadCell>Hour</TableHeadCell>
                  <TableHeadCell>Latitude</TableHeadCell>
                  <TableHeadCell>Longitude</TableHeadCell>
                  <TableHeadCell>Speed (m/s)</TableHeadCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {predictions.map((p, i) => (
                  <TableRow key={i}>
                    <TableCell>{p.hour ?? i}</TableCell>
                    <TableCell className="tabular-nums">
                      {p.latitude?.toFixed(5)}
                    </TableCell>
                    <TableCell className="tabular-nums">
                      {p.longitude?.toFixed(5)}
                    </TableCell>
                    <TableCell>{p.estimated_speed ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <div className="rounded-md border-l-4 border-primary bg-slate-50 p-3 text-sm">
              Estimated drift over <strong>{hours}</strong> hours:{" "}
              <strong className="tabular-nums">{totalKm} km</strong>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default DriftPanel;
