import { useCallback } from "react";
import api from "../services/api";
import { API_URL, POLL_INTERVAL } from "../config";
import { usePolling } from "../hooks/usePolling";
import PageHeader from "../components/ui/PageHeader";
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
import { SkeletonRows } from "../components/ui/Skeleton";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeadCell,
  TableCell,
} from "../components/ui/Table";
import { riskTone } from "../components/ui/tone";
import { IconDownload, IconFileText } from "../components/ui/icons";

function Reports() {
  const historyFetcher = useCallback(
    () => api.get("/monitoring/history").then((r) => r.data),
    [],
  );
  const { data: history, error, loading } = usePolling(
    historyFetcher,
    POLL_INTERVAL,
  );

  const incidents = history?.incidents ?? [];
  const reportUrl = `${API_URL}/report/generate`;
  const latestReportUrl = `${API_URL}/report/latest`;

  return (
    <div>
      <PageHeader
        title="Incident Reports"
        description="Auto-generated PDF reports for every detected spill"
      />

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Generate Report</CardTitle>
          <IconFileText className="text-muted" />
        </CardHeader>
        <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button
            href={latestReportUrl}
            target="_blank"
            rel="noreferrer"
            icon={<IconDownload />}
          >
            Download latest PDF
          </Button>
          <Button
            variant="outline"
            href={reportUrl}
            target="_blank"
            rel="noreferrer"
          >
            Regenerate from latest data
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detected Incidents</CardTitle>
        </CardHeader>
        <CardContent>
          {loading && !history ? (
            <SkeletonRows rows={5} />
          ) : error && !history ? (
            <ErrorState message="Incident history is unavailable." />
          ) : incidents.length === 0 ? (
            <EmptyState title="No incidents yet" />
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeadCell>Incident ID</TableHeadCell>
                  <TableHeadCell>Detected At</TableHeadCell>
                  <TableHeadCell>Area</TableHeadCell>
                  <TableHeadCell>Risk</TableHeadCell>
                  <TableHeadCell>Location</TableHeadCell>
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
                        {new Date(inc.detected_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="tabular-nums">
                        {inc.spill_area_km2} km²
                      </TableCell>
                      <TableCell>
                        <Badge variant={riskTone(inc.risk_level)}>
                          {inc.risk_level}
                        </Badge>
                      </TableCell>
                      <TableCell className="tabular-nums">
                        {inc.latitude}, {inc.longitude}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default Reports;
