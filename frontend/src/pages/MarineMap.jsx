import "leaflet/dist/leaflet.css";

import { useCallback } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  CircleMarker,
} from "react-leaflet";

import api from "../services/api";
import { POLL_INTERVAL } from "../config";
import { usePolling } from "../hooks/usePolling";
import { useIncidentLocation, TN_FALLBACK_LOCATION } from "../hooks/useIncidentLocation";
import PageHeader from "../components/ui/PageHeader";
import Badge from "../components/ui/Badge";
import Stat from "../components/ui/Stat";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import RadarSweep from "../components/ui/3d/RadarSweep";
import { IconDroplet, IconShip, IconMap } from "../components/ui/icons";

function MarineMap() {
  const statusFetcher = useCallback(
    () => api.get("/monitoring/status").then((r) => r.data),
    [],
  );
  const vesselsFetcher = useCallback(
    () => api.get("/ais/suspect-vessels").then((r) => r.data),
    [],
  );
  const driftFetcher = useCallback(
    () => api.get("/drift/predict").then((r) => r.data),
    [],
  );

  const { data: status } = usePolling(statusFetcher, POLL_INTERVAL);
  const { data: vesselsData } = usePolling(vesselsFetcher, POLL_INTERVAL);
  const { data: driftData } = usePolling(driftFetcher, POLL_INTERVAL);

  const { location: incidentLocation } = useIncidentLocation();

  const last = status?.last_detection;
  const center = last ? [last.latitude, last.longitude] : [incidentLocation.lat, incidentLocation.lon];
  const spill = last ? [last.latitude, last.longitude] : [incidentLocation.lat, incidentLocation.lon];
  const vessels = (vesselsData?.vessels ?? []).slice(0, 10);
  const drift = (driftData?.predictions ?? []).map((p) => [
    p.latitude,
    p.longitude,
  ]);

  return (
    <div>
      <PageHeader
        title="Marine Operations Map"
        description="Live spill position, suspect vessels and the 24-hour drift forecast"
        badge={
          <Badge variant="success" dot>
            Live
          </Badge>
        }
      />

      <div className="relative mb-6 overflow-hidden rounded-xl border border-border shadow-card">
        <div className="h-[520px] w-full lg:h-[620px]">
          <MapContainer
            center={center}
            zoom={9}
            style={{ height: "100%", width: "100%" }}
          >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

            {/* Oil spill */}
            <Marker position={spill}>
              <Popup>
                <div className="text-sm font-semibold">Oil Spill</div>
                <div className="text-xs">Status: ACTIVE</div>
                {last && (
                  <>
                    <div className="text-xs">Confidence: {last.confidence}%</div>
                    <div className="text-xs">
                      Area: {last.spill_area_km2} km²
                    </div>
                  </>
                )}
                <div className="text-xs">Incident: {last?.id ?? "—"}</div>
              </Popup>
            </Marker>

            {/* Suspect vessels */}
            {vessels.map((vessel, index) => (
              <CircleMarker
                key={vessel.MMSI ?? index}
                center={[vessel.LAT, vessel.LON]}
                radius={7}
                pathOptions={{
                  color: index === 0 ? "#0d9488" : "#0891b2",
                  fillColor: index === 0 ? "#0d9488" : "#38bdf8",
                  fillOpacity: 1,
                }}
              >
                <Popup>
                  <div className="text-sm font-semibold">
                    {vessel.VesselName ?? vessel.MMSI}
                  </div>
                  <div className="text-xs">MMSI: {vessel.MMSI}</div>
                  <div className="text-xs">Speed: {vessel.SOG} knots</div>
                  <div className="text-xs">Heading: {vessel.COG}°</div>
                  <div className="text-xs">
                    Suspect Score: {vessel.SuspectScore}
                  </div>
                </Popup>
              </CircleMarker>
            ))}

            {/* Drift line + forecast points */}
            {drift.length > 1 && (
              <Polyline
                positions={drift}
                pathOptions={{ color: "#0d9488", weight: 4, dashArray: "8 8" }}
              />
            )}
            {drift.map((point, index) => (
              <CircleMarker
                key={index}
                center={point}
                radius={6}
                pathOptions={{
                  color: "#dc2626",
                  fillColor: "#f87171",
                  fillOpacity: 1,
                }}
              >
                <Popup>
                  <div className="text-sm font-semibold">Drift Forecast</div>
                  <div className="text-xs">Hour {index + 1}</div>
                  <div className="text-xs">Latitude: {point[0]}</div>
                  <div className="text-xs">Longitude: {point[1]}</div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
        <RadarSweep className="z-[1]" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Marine Situation Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Stat
              label="Oil Spill Status"
              value={last ? "Active" : "Scanning"}
              tone={last ? "danger" : "success"}
              icon={<IconDroplet />}
            />
            <Stat
              label="Ranked Vessels"
              value={vesselsData?.count ?? 0}
              tone="info"
              icon={<IconShip />}
            />
            <Stat
              label="Drift Forecast"
              value={`${drift.length} pts`}
              tone="info"
              icon={<IconMap />}
            />
            <Stat
              label="Spill Location"
              value={`${spill[0]}, ${spill[1]}`}
              tone="default"
              icon={<IconMap />}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default MarineMap;
