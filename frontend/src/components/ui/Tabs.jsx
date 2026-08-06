import { createContext, useContext, useState } from "react";
import { cn } from "../../lib/cn";

const TabsContext = createContext(null);

export function Tabs({
  value,
  onValueChange,
  defaultValue,
  className,
  children,
}) {
  const [internal, setInternal] = useState(defaultValue);
  const active = value ?? internal;
  const setActive = (v) => {
    if (value === undefined) setInternal(v);
    onValueChange?.(v);
  };
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({ className, children }) {
  return (
    <div
      className={cn("inline-flex rounded-md bg-slate-100 p-1 gap-1", className)}
    >
      {children}
    </div>
  );
}

export function TabsTrigger({ value, className, children }) {
  const { active, setActive } = useContext(TabsContext);
  const isActive = active === value;
  return (
    <button
      type="button"
      role="tab"
      aria-selected={isActive}
      onClick={() => setActive(value)}
      className={cn(
        "px-3 py-1.5 text-sm rounded-md transition-colors",
        isActive
          ? "bg-white shadow-sm text-foreground font-medium"
          : "text-muted hover:text-foreground",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, className, children }) {
  const { active } = useContext(TabsContext);
  if (active !== value) return null;
  return (
    <div role="tabpanel" className={cn("mt-4", className)}>
      {children}
    </div>
  );
}
