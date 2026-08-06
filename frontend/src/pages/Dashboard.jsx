import { lazy, Suspense } from "react";
import PageHeader from "../components/ui/PageHeader";
import Badge from "../components/ui/Badge";
import StatsRow from "../components/dashboard/StatsRow";
import SpillCards from "../components/Cards/SpillCards";
import AISPanel from "../components/Cards/AISPanel";
import VesselRanking from "../components/Cards/VesselRanking";
import AISReplay from "../components/Cards/AISReplay";
import DriftPanel from "../components/Cards/DriftPanel";
import WeatherPanel from "../components/Cards/WeatherPanel";
import MapPreview from "../components/Cards/MapPreview";
import MissionSummary from "../components/Cards/MissionSummary";
import ImpactPanel from "../components/Cards/ImpactPanel";
import RiskGauge from "../components/Analytics/RiskGauge";
import SpillTrend from "../components/Analytics/SpillTrend";
import EconomicChart from "../components/Analytics/EconomicChart";
import CleanupPanel from "../components/dashboard/CleanupPanel";
import AlertPanel from "../components/Alerts/AlertPanel";
import SystemCheck from "./SystemCheck";

// three.js is heavy — lazy-load so it only ships to the Dashboard.
const OceanGlobe = lazy(() => import("../components/ui/3d/OceanGlobe"));

function Dashboard() {
  return (
    <div>
      <PageHeader
        title="Command Dashboard"
        description="Live marine intelligence — oil spill, vessel, weather and impact monitoring"
        badge={
          <Badge variant="success" dot>
            Live
          </Badge>
        }
      />

      <StatsRow />
      <SpillCards />

      {/* Situation hero: 3D globe + mission + impact */}
      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="flex flex-col items-center justify-center rounded-xl border border-border bg-ocean-950 p-6 text-center text-white shadow-card">
          <Suspense
            fallback={
              <div className="size-[220px] animate-pulse rounded-full bg-ocean-800" />
            }
          >
            <OceanGlobe size={220} />
          </Suspense>
          <div className="mt-4 text-sm font-semibold text-teal-200">
            Global Incident View
          </div>
          <div className="mt-1 text-xs text-slate-300">
            Live spill position on the ocean globe
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:col-span-2">
          <MissionSummary />
          <ImpactPanel />
        </div>
      </div>

      {/* Analytics + operational panels */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
        <AISPanel />
        <VesselRanking />
        <AISReplay />
        <DriftPanel />
        <WeatherPanel />
        <MapPreview />
        <RiskGauge />
        <SpillTrend />
        <EconomicChart />
        <CleanupPanel />
      </div>

      <div className="mt-6">
        <AlertPanel />
      </div>

      <div className="mt-6">
        <SystemCheck />
      </div>
    </div>
  );
}

export default Dashboard;
