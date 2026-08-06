import { useEffect, useState } from "react";
import axios from "axios";
import api from "../services/api";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import Stat from "../components/ui/Stat";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import { SkeletonRows } from "../components/ui/Skeleton";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeadCell,
  TableCell,
} from "../components/ui/Table";
import { IconActivity } from "../components/ui/icons";

const ENDPOINTS = [
  { name: "Impact Assessment API", url: "/impact/summary" },
  { name: "Environmental Analysis", url: "/impact/environment" },
  { name: "Economic Assessment", url: "/impact/economic" },
  { name: "Risk Assessment Engine", url: "/impact/risk" },
  { name: "AIS Vessel Tracking", url: "/ais/nearby-vessels" },
];

function SystemCheck() {
  const [results, setResults] = useState([]);
  const [checkedAt, setCheckedAt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function checkOne(endpoint) {
      try {
        const source = axios.CancelToken.source();
        const timer = setTimeout(() => source.cancel(), 10000);
        await api.get(endpoint.url, { cancelToken: source.token });
        clearTimeout(timer);
        return { ...endpoint, status: "ONLINE" };
      } catch {
        return { ...endpoint, status: "OFFLINE" };
      }
    }

    async function checkSystem() {
      const checks = await Promise.all(ENDPOINTS.map(checkOne));
      if (!cancelled) {
        setResults(checks);
        setCheckedAt(new Date());
        setLoading(false);
      }
    }

    checkSystem();
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const online = results.filter((r) => r.status === "ONLINE").length;
  const healthy = results.length > 0 && online === results.length;

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Health & Operational Status</CardTitle>
        <Badge variant={healthy ? "success" : "danger"} dot>
          {results.length === 0
            ? "Checking…"
            : healthy
              ? "System Healthy"
              : "Attention Required"}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Stat
            label="Operational Services"
            value={results.length ? `${online}/${results.length}` : "—"}
            tone={healthy ? "success" : "danger"}
            icon={<IconActivity />}
          />
          <Stat
            label="Last Health Check"
            value={checkedAt ? checkedAt.toLocaleTimeString() : "—"}
            tone="default"
          />
        </div>

        {loading && results.length === 0 ? (
          <SkeletonRows rows={5} />
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableHeadCell>System Module</TableHeadCell>
                <TableHeadCell>Status</TableHeadCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {results.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        item.status === "ONLINE" ? "success" : "danger"
                      }
                    >
                      {item.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setLoading(true);
            setRefreshKey((k) => k + 1);
          }}
          disabled={loading}
        >
          {loading ? "Checking…" : "Refresh"}
        </Button>
      </CardContent>
    </Card>
  );
}

export default SystemCheck;
