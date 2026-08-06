import { useCallback } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import { Skeleton } from "../ui/Skeleton";
import ErrorState from "../ui/ErrorState";
import { riskBandColor } from "../ui/chartColors";
import { riskTone } from "../ui/tone";

function RiskGauge() {
  const fetcher = useCallback(
    () => api.get("/impact/risk").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const risk = Number(data?.["Risk Score"] ?? 0);
  const level = String(data?.["Risk Level"] ?? "—").replace(/[^\w\s]/g, "");
  const color = riskBandColor(risk);

  const gaugeData = [{ value: risk }, { value: 100 - risk }];

  if (loading && !data)
    return (
      <Card>
        <CardContent>
          <Skeleton className="mx-auto h-64 w-64 rounded-full" />
        </CardContent>
      </Card>
    );

  if (error && !data)
    return (
      <Card>
        <CardContent>
          <ErrorState message="Risk assessment is unavailable." />
        </CardContent>
      </Card>
    );

  return (
    <Card>
      <CardHeader>
        <CardTitle>National Marine Risk Index</CardTitle>
        <Badge variant={riskTone(level)}>{level.trim() || "—"}</Badge>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        <div className="relative h-52 w-52">
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={gaugeData}
                dataKey="value"
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={90}
                startAngle={90}
                endAngle={-270}
                stroke="none"
              >
                <Cell fill={color} />
                <Cell fill="#e2e8f0" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-4xl font-bold tabular-nums" style={{ color }}>
              {risk}
            </div>
            <div className="text-xs text-muted">Risk Index</div>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap justify-center gap-x-4 gap-y-1 text-xs">
          {[
            { name: "LOW", color: "#059669" },
            { name: "MODERATE", color: "#facc15" },
            { name: "HIGH", color: "#f97316" },
            { name: "CRITICAL", color: "#dc2626" },
          ].map((item) => (
            <span key={item.name} className="flex items-center gap-1.5">
              <span
                className="size-2 rounded-full"
                style={{ background: item.color }}
                aria-hidden="true"
              />
              <span className="text-muted">{item.name}</span>
            </span>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default RiskGauge;
