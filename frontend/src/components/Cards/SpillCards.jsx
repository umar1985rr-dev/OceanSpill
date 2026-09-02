import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import Stat from "../ui/Stat";
import ErrorState from "../ui/ErrorState";
import { SkeletonCard } from "../ui/Skeleton";
import { riskTone } from "../ui/tone";
import {
  IconAlertTriangle,
  IconMap,
  IconShip,
  IconDroplet,
} from "../ui/icons";

function SpillCards() {
  const fetcher = useCallback(
    () => api.get("/impact/summary").then((r) => r.data),
    [],
  );
  const { data, error, loading } = usePolling(fetcher, POLL_INTERVAL);

  if (loading && !data) return <SkeletonCard />;
  if (error && !data) return <ErrorState message="Impact summary is unavailable." />;

  const fmtMoney = (v) =>
    v != null ? `$${Number(v).toLocaleString()}` : "—";

  const cards = [
    {
      label: "Risk Score",
      value: data?.["Risk Score"] ?? "—",
      tone: riskTone(data?.["Risk Level"]),
      icon: <IconAlertTriangle />,
    },
    {
      label: "Risk Level",
      value: data?.["Risk Level"] ?? "—",
      tone: riskTone(data?.["Risk Level"]),
      icon: <IconShip />,
    },
    {
      label: "Nearest Coastline",
      value: data?.["Nearest Coastline"] != null ? `${data["Nearest Coastline"]} km` : "—",
      tone: "info",
      icon: <IconMap />,
    },
    {
      label: "Cleanup Cost",
      value: fmtMoney(data?.["Cleanup Cost"]),
      tone: "warning",
      icon: <IconDroplet />,
    },
  ];

  return (
    <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((c) => (
        <Stat key={c.label} {...c} />
      ))}
    </div>
  );
}

export default SpillCards;
