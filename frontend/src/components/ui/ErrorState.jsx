import Button from "./Button";
import { IconAlertTriangle } from "./icons";

export default function ErrorState({
  title = "Unable to reach the data service",
  message,
  retry,
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 p-10 text-center">
      <div className="rounded-full bg-red-50 p-3 text-danger" aria-hidden="true">
        <IconAlertTriangle />
      </div>
      <p className="text-sm font-medium text-foreground">{title}</p>
      {message && <p className="max-w-sm text-sm text-muted">{message}</p>}
      {retry && (
        <Button variant="outline" size="sm" className="mt-2" onClick={retry}>
          Retry
        </Button>
      )}
    </div>
  );
}
