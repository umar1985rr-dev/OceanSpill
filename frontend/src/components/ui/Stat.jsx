import { cn } from "../../lib/cn";

const tones = {
  default: "text-foreground",
  success: "text-success",
  warning: "text-warning",
  danger: "text-danger",
  info: "text-info",
};

/** KPI tile: eyebrow label + large tabular-nums value + optional tone/hint. */
export default function Stat({
  label,
  value,
  icon,
  tone = "default",
  hint,
  className,
  ...rest
}) {
  return (
    <div
      className={cn(
        "bg-surface rounded-xl border border-border shadow-card p-5 flex flex-col gap-1.5",
        className,
      )}
      {...rest}
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-xs font-medium uppercase tracking-wide text-muted">
          {label}
        </span>
        {icon && (
          <span className="text-muted" aria-hidden="true">
            {icon}
          </span>
        )}
      </div>
      <div className={cn("text-2xl font-bold tabular-nums leading-tight", tones[tone])}>
        {value}
      </div>
      {hint && <div className="text-xs text-muted">{hint}</div>}
    </div>
  );
}
