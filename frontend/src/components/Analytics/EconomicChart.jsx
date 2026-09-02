import { useCallback } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
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
import { CHART_COLORS } from "../ui/chartColors";

function EconomicChart() {
  const fetcher = useCallback(
    () => api.get("/impact/economic").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  const dataItems = [
    { name: "Cleanup Operations", value: data?.["Cleanup Cost ($)"] ?? 0 },
    { name: "Fisheries", value: data?.["Estimated Fisheries Loss ($)"] ?? 0 },
    { name: "Shipping", value: data?.["Estimated Shipping Loss ($)"] ?? 0 },
    { name: "Tourism", value: data?.["Estimated Tourism Loss ($)"] ?? 0 },
  ];
  const totalLoss = dataItems.reduce(
    (s, item) => s + (Number(item.value) || 0),
    0,
  );

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
          <ErrorState message="Economic assessment is unavailable." />
        </CardContent>
      </Card>
    );

  if (totalLoss === 0)
    return (
      <Card>
        <CardContent>
          <EmptyState title="No economic data yet" />
        </CardContent>
      </Card>
    );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Economic Damage Assessment</CardTitle>
        <Badge variant="outline">USD</Badge>
      </CardHeader>
      <CardContent>
        <div className="h-64 w-full">
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={dataItems}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={2}
                stroke="#ffffff"
                strokeWidth={2}
              >
                {dataItems.map((_, index) => (
                  <Cell
                    key={index}
                    fill={CHART_COLORS[index % CHART_COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(v) => `$${Number(v).toLocaleString()}`}
                contentStyle={{
                  borderRadius: 8,
                  border: "1px solid #e2e8f0",
                  fontSize: 13,
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {totalLoss > 0 && (
          <div className="mt-3 rounded-md bg-red-50 p-3 text-center text-sm font-bold tabular-nums text-danger">
            Total Estimated Loss: ${totalLoss.toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default EconomicChart;
