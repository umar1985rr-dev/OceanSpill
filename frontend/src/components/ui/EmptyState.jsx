export default function EmptyState({ title, description, icon, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 p-10 text-center">
      {icon && (
        <div className="rounded-full bg-slate-100 p-3 text-muted" aria-hidden="true">
          {icon}
        </div>
      )}
      <p className="text-sm font-medium text-foreground">{title}</p>
      {description && (
        <p className="max-w-sm text-sm text-muted">{description}</p>
      )}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
