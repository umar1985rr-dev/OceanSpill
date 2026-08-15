import { cn } from "../../lib/cn";

/** Responsive table primitives. `Table` wraps content in an overflow container. */
export function Table({ className, children, ...props }) {
  return (
    <div className="overflow-x-auto">
      <table
        className={cn("w-full text-sm min-w-[640px] border-collapse", className)}
        {...props}
      >
        {children}
      </table>
    </div>
  );
}

export function TableHead({ className, ...props }) {
  return <thead className={className} {...props} />;
}

export function TableHeadCell({ className, ...props }) {
  return (
    <th
      className={cn(
        "bg-slate-50 px-3 py-2.5 text-left text-xs uppercase tracking-wide text-muted font-semibold",
        className,
      )}
      {...props}
    />
  );
}

export function TableBody({ className, ...props }) {
  return <tbody className={className} {...props} />;
}

export function TableRow({ className, ...props }) {
  return (
    <tr
      className={cn("border-b border-border hover:bg-slate-50", className)}
      {...props}
    />
  );
}

export function TableCell({ className, ...props }) {
  return (
    <td className={cn("px-3 py-2.5 align-middle", className)} {...props} />
  );
}

export function TableEmptyRow({ colSpan, children }) {
  return (
    <tr>
      <td colSpan={colSpan}>{children}</td>
    </tr>
  );
}
