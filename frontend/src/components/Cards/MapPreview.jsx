import { lazy, Suspense, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Button from "../ui/Button";
import Tilt from "../ui/3d/Tilt";
import { IconMap } from "../ui/icons";

const OceanWaves = lazy(() => import("../ui/3d/OceanWaves"));

function MapPreview() {
  const navigate = useNavigate();
  const fetcher = useCallback(
    () => api.get("/monitoring/status").then((r) => r.data),
    [],
  );
  const { data } = usePolling(fetcher, POLL_INTERVAL);
  const last = data?.last_detection;

  const location = last
    ? `${last.latitude?.toFixed(4)}, ${last.longitude?.toFixed(4)}`
    : "Awaiting detection…";

  return (
    <Tilt>
      <Card>
        <CardHeader>
          <CardTitle>Marine Situation Map</CardTitle>
          <IconMap className="text-muted" />
        </CardHeader>
        <CardContent>
          <div className="relative overflow-hidden rounded-lg bg-ocean-900">
            <Suspense
              fallback={<div className="h-[140px] animate-pulse bg-ocean-800" />}
            >
              <OceanWaves className="relative z-0" height={140} />
            </Suspense>
            <div className="absolute inset-0 z-10 flex flex-col items-center justify-center text-center text-white">
              <div className="text-lg font-bold">Interactive Marine Map</div>
              <div className="mt-1 text-sm text-slate-300">
                Oil Spill · AIS Vessels · Drift Forecast
              </div>
              <div className="mt-1 font-mono text-xs text-teal-200">
                Latest: {location}
              </div>
            </div>
          </div>

          <Button
            className="mt-4 w-full"
            onClick={() => navigate("/marine-map")}
          >
            Open Full Marine Map
          </Button>
        </CardContent>
      </Card>
    </Tilt>
  );
}

export default MapPreview;
