import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { useSharedPolling } from "../../hooks/useSharedPolling";
import Stat from "../ui/Stat";
import { riskTone } from "../ui/tone";
import { IconDroplet, IconActivity, IconAlertTriangle, IconLayers } from "../ui/icons";

function StatsRow() {
  const fetcher = useCallback(
    () => api.get("/monitoring/status").then((r) => r.data),
    [],
  );
  const { data } = useSharedPolling(fetcher, POLL_INTERVAL, "monitoring-status");
  const last = data?.last_detection;

  const stats = [
    {
      label: "Oil Spill Status",
      value: last ? "Detected" : "Scanning",
      tone: last ? "danger" : "success",
      icon: <IconDroplet />,
    },
    {
      label: "Detection Confidence",
      value: last ? `${last.confidence}%` : "—",
      tone: "default",
      icon: <IconActivity />,
    },
    {
      label: "Risk Level",
      value: last ? last.risk_level : "—",
      tone: last ? riskTone(last.risk_level) : "default",
      icon: <IconAlertTriangle />,
    },
    {
      label: "Detection Engine",
      value: "U-Net",
      tone: "info",
      icon: <IconLayers />,
    },
  ];

  return (
    <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((s) => (
        <Stat key={s.label} {...s} />
      ))}
    </div>
  );
}

export default StatsRow;
