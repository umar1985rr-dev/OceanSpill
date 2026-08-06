import { cn } from "../../lib/cn";

const variants = {
  neutral: "bg-slate-100 text-slate-600",
  success: "bg-emerald-50 text-emerald-700",
  warning: "bg-amber-50 text-amber-700",
  danger: "bg-red-50 text-red-700",
  info: "bg-cyan-50 text-cyan-700",
  outline: "border border-slate-300 text-slate-600",
};

export default function Badge({
  variant = "neutral",
  dot = false,
  className,
  children,
  ...rest
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold whitespace-nowrap",
        variants[variant],
        className,
      )}
      {...rest}
    >
      {dot && (
        <span
          className="size-1.5 rounded-full bg-current"
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
}
