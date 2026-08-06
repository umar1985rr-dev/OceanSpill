import { useState } from "react";
import { NavLink } from "react-router-dom";
import { IconMenu, IconX, IconDroplet } from "../ui/icons";
import { cn } from "../../lib/cn";
import { NAV_ITEMS } from "./nav";

export default function Topbar() {
  const [open, setOpen] = useState(false);

  return (
    <div className="sticky top-0 z-40 flex items-center justify-between border-b border-white/10 bg-ocean-950 px-4 py-3 text-white lg:hidden">
      <div className="flex items-center gap-2.5">
        <div className="flex size-8 items-center justify-center rounded-md bg-primary/25">
          <IconDroplet className="text-teal-400" />
        </div>
        <span className="text-sm font-bold tracking-tight">OceanSpill</span>
      </div>

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close menu" : "Open menu"}
        className="rounded-md p-2 hover:bg-white/10"
      >
        {open ? <IconX /> : <IconMenu />}
      </button>

      {open && (
        <nav className="absolute inset-x-0 top-full space-y-1 border-t border-white/10 bg-ocean-950 p-3 shadow-lg">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium",
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
      )}
    </div>
  );
}
