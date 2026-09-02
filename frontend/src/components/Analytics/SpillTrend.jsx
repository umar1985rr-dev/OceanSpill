import { useCallback } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { Skeleton } from "../ui/Skeleton";

function SpillTrend() {
  const fetcher = useCallback(
    () => api.get("/monitoring/history").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const incidents = data?.incidents ?? [];

  // X-axis is the real detection timestamp (local time), not an ordinal.
  // Monotonic detection order is preserved whether or not the sample runs
  // land on evenly spaced intervals.
  const chartData = incidents.slice(-8).map((inc) => {
    const t = new Date(inc.detected_at);
    return {
      time: t,
      timeLabel: Number.isNaN(t.getTime()) ? "—" : t.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      area: inc.spill_area_km2,
    };
  });

  if (loading && !data)
    return (
      <Card>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    );

  if (error && !data)
    return (
      <Card>
        <CardContent>
          <ErrorState message="Detection history is unavailable." />
        </CardContent>
      </Card>
    );

  if (chartData.length === 0)
    return (
      <Card>
        <CardContent>
          <EmptyState title="No detections to chart yet" />
        </CardContent>
      </Card>
    );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Spill Area Trend (Detections)</CardTitle>
        <Badge variant="success" dot>
          Live
        </Badge>
      </CardHeader>
      <CardContent>
        <div className="h-64 w-full">
          <ResponsiveContainer>
            <LineChart
              data={chartData}
              margin={{ top: 8, right: 8, bottom: 0, left: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#e2e8f0"
                vertical={false}
              />
              <XAxis
                dataKey="timeLabel"
                tick={{ fontSize: 12, fill: "#64748b" }}
                tickLine={false}
                axisLine={{ stroke: "#cbd5e1" }}
                interval={window.innerWidth < 768 ? 1 : 0}
              />
              <YAxis
                tick={{ fontSize: 12, fill: "#64748b" }}
                tickLine={false}
                axisLine={false}
                width={44}
              />
              <Tooltip
                formatter={(v) => [`${v} km²`, "Spill Area"]}
                labelFormatter={(l, payload) => {
                  const t = payload?.[0]?.payload?.time;
                  return Number.isNaN(t?.getTime())
                    ? "No timestamp"
                    : t.toLocaleString();
                }}
                contentStyle={{
                  borderRadius: 8,
                  border: "1px solid #e2e8f0",
                  fontSize: 13,
                }}
              />
              <Line
                type="monotone"
                dataKey="area"
                stroke="#0d9488"
                strokeWidth={2}
                dot={{ fill: "#0d9488", r: 3, strokeWidth: 0 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export default SpillTrend;
