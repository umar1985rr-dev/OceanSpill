import { useEffect, useRef } from "react";
import api from "../services/api";
import { EVENT_POLL_INTERVAL } from "../config";

/** Window event every polled component listens to. */
export const REFRESH_EVENT = "oceanspill:refresh";

/**
 * Watches the backend event version + process instance id and dispatches a
 * `oceanspill:refresh` window event whenever either changes:
 *
 *  - version bumps  -> a new oil spill was detected (report is ready)
 *  - instance_id changes -> the backend was started / restarted
 *
 * Mounted once in <Layout>, so every usePolling() panel on every page refetches
 * immediately when an event arrives (instead of waiting for its next poll tick).
 */
export function useBackendEvents() {
  const lastRef = useRef(null);

  useEffect(() => {
    async function poll() {
      let next;
      try {
        const res = await api.get("/monitoring/status");
        next = {
          instanceId: res.data?.instance_id,
          version: res.data?.version,
        };
      } catch {
        return; // backend unreachable — nothing to compare yet
      }

      const prev = lastRef.current;
      if (
        prev &&
        (prev.instanceId !== next.instanceId || prev.version !== next.version)
      ) {
        window.dispatchEvent(
          new CustomEvent(REFRESH_EVENT, { detail: next }),
        );
      }
      lastRef.current = next;
    }

    poll();
    const id = setInterval(poll, EVENT_POLL_INTERVAL);
    return () => clearInterval(id);
  }, []);
}
