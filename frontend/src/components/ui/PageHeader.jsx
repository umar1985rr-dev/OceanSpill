export default function PageHeader({ title, description, badge, children }) {
  return (
    <div className="mb-6 flex flex-col gap-1 md:flex-row md:items-end md:justify-between">
      <div className="min-w-0">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
          {badge}
        </div>
        {description && (
          <p className="mt-1 max-w-prose text-sm text-muted">{description}</p>
        )}
      </div>
      {children && (
        <div className="mt-3 flex items-center gap-2 md:mt-0">{children}</div>
      )}
    </div>
  );
}
