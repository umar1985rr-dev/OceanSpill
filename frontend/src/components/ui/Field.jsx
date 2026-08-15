import { cn } from "../../lib/cn";

/** Label/value pair for card body grids. */
export function Field({ label, value, mono }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-muted">
        {label}
      </dt>
      <dd className={cn("mt-0.5 text-sm", mono && "tabular-nums")}>{value}</dd>
    </div>
  );
}

export function FieldGrid({ className, children }) {
  return (
    <dl className={cn("grid grid-cols-2 gap-x-4 gap-y-3 text-sm", className)}>
      {children}
    </dl>
  );
}
