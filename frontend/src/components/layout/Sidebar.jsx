import { NavLink } from "react-router-dom";
import { useCallback } from "react";
import api from "../../services/api";
import { POLL_INTERVAL } from "../../config";
import { usePolling } from "../../hooks/usePolling";
import { IconDroplet } from "../ui/icons";
import { cn } from "../../lib/cn";
import { NAV_ITEMS } from "./nav";
import { useAuth } from "../../context/AuthContext";

function StatusPill() {
  const fetcher = useCallback(
    () => api.get("/monitoring/status").then((r) => r.data),
    [],
  );
  const { data, error } = usePolling(fetcher, POLL_INTERVAL);

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-xs font-medium text-amber-400">
        <span className="size-2 rounded-full bg-amber-500" aria-hidden="true" />
        Backend offline
      </div>
    );
  }

  const running = data?.is_running === true;
  const frames = data?.feed?.frames_served ?? 0;

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium",
        running ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400",
      )}
    >
      <span
        className={cn(
          "size-2 animate-pulse rounded-full",
          running ? "bg-emerald-500" : "bg-red-500",
        )}
        aria-hidden="true"
      />
      {running ? `Live monitoring · ${frames} frames` : "Monitoring stopped"}
    </div>
  );
}

export default function Sidebar({ onNavigate }) {
  const { logout } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col bg-ocean-950 text-white lg:flex">
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="flex size-10 items-center justify-center rounded-lg bg-primary/25">
          <IconDroplet className="text-teal-400" />
        </div>
        <div className="leading-tight">
          <div className="text-base font-bold tracking-tight">OceanSpill</div>
          <div className="text-xs text-slate-400">Marine Intelligence</div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-teal-600/15 text-teal-300"
                  : "text-slate-300 hover:bg-white/5 hover:text-white",
              )
            }
          >
            <Icon className="size-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto border-t border-white/10 p-3 space-y-3">
        <StatusPill />
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition"
        >
          <svg
            width={20}
            height={20}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.8}
            strokeLinecap="round"
            strokeLinejoin="round"
            className="size-4"
            aria-hidden="true"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          Sign Out
        </button>
      </div>
    </aside>
  );
}
