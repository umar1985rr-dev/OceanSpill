import { cn } from "../../lib/cn";

export function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-slate-200/70", className)}
      {...props}
    />
  );
}

export function SkeletonRows({ rows = 4, className }) {
  return (
    <div className={cn("space-y-3", className)}>
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton
          key={i}
          className={cn("h-4", i === 0 ? "w-3/4" : i % 2 ? "w-1/2" : "w-2/3")}
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className }) {
  return (
    <div
      className={cn(
        "bg-surface rounded-xl border border-border shadow-card p-5 space-y-3",
        className,
      )}
    >
      <Skeleton className="h-4 w-1/3" />
      <SkeletonRows rows={3} />
    </div>
  );
}
