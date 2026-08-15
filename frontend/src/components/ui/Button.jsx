import { cn } from "../../lib/cn";
import { IconSpinner } from "./icons";

const variants = {
  primary: "bg-primary text-primary-foreground hover:bg-primary-hover",
  secondary: "bg-slate-100 text-slate-700 hover:bg-slate-200",
  outline: "border border-slate-300 text-slate-700 hover:bg-slate-50",
  ghost: "text-slate-600 hover:bg-slate-100",
  danger: "bg-danger text-white hover:bg-red-700",
};

const sizes = {
  sm: "h-8 px-3 text-xs gap-1.5",
  md: "h-9 px-4 text-sm gap-2",
  lg: "h-10 px-5 text-sm gap-2",
};

/**
 * Button / link-button.
 * Pass `href` (and optionally `target`) to render an <a> instead.
 */
export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  href,
  className,
  children,
  disabled,
  ...rest
}) {
  const classes = cn(
    "inline-flex items-center justify-center font-semibold rounded-md transition-colors",
    "disabled:opacity-50 disabled:pointer-events-none",
    "focus-visible:outline-2 focus-visible:outline-offset-2",
    variants[variant],
    sizes[size],
    className,
  );

  const content = (
    <>
      {loading ? (
        <IconSpinner className="size-4 animate-spin" />
      ) : (
        icon
      )}
      {children}
    </>
  );

  if (href) {
    return (
      <a href={href} className={classes} {...rest}>
        {content}
      </a>
    );
  }

  return (
    <button
      type="button"
      disabled={disabled || loading}
      className={classes}
      {...rest}
    >
      {content}
    </button>
  );
}
