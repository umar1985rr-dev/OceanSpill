import { cn } from "../../../lib/cn";

/** CSS-only rotating radar sweep overlay (2.5D motion, zero dependencies). */
export default function RadarSweep({ className }) {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 overflow-hidden rounded-xl",
        className,
      )}
      aria-hidden="true"
    >
      <div className="absolute inset-0 animate-radar [background:conic-gradient(from_0deg,rgba(13,148,136,0)_0deg,rgba(13,148,136,0.16)_60deg,rgba(13,148,136,0)_120deg)]" />
      <div className="absolute inset-0 rounded-xl border border-teal-600/20" />
    </div>
  );
}
