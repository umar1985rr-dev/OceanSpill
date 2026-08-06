import { useEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { useBackendEvents } from "../../hooks/useBackendEvents";

export default function Layout() {
  const { pathname } = useLocation();

  // Watch for new detections / backend (re)starts and refresh every panel.
  useBackendEvents();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [pathname]);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Sidebar />

      <div className="flex min-h-screen flex-1 flex-col lg:pl-64">
        <Topbar />

        <main className="mx-auto w-full max-w-[1400px] flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>

        <footer className="border-t border-border bg-surface py-6 text-center text-xs text-muted">
          OceanSpill · Marine Intelligence Platform — AI-powered oil spill
          detection &amp; response support
        </footer>
      </div>
    </div>
  );
}
