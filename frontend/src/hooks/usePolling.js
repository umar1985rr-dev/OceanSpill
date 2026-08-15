import { useEffect, useRef, useState } from "react";

import { REFRESH_EVENT } from "./useBackendEvents";

/**
 * Poll an async fetcher every `interval` ms.
 *
 * @param {() => Promise<any>} fetcher - returns fresh data
 * @param {number} interval - poll interval in ms
 * @param {boolean} enabled - pause polling while false
 */
export function usePolling(fetcher, interval, enabled = true) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const fetcherRef = useRef(fetcher);

  useEffect(() => {
    fetcherRef.current = fetcher;
  }, [fetcher]);

  useEffect(() => {
    if (!enabled) {
      return undefined;
    }

    let cancelled = false;

    const run = async () => {
      try {
        const result = await fetcherRef.current();
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    run();
    const id = setInterval(run, interval);

    // When the backend signals a new detection or a (re)start, refetch right
    // away instead of waiting for the next interval tick.
    const onRefresh = () => {
      if (!cancelled) run();
    };
    window.addEventListener(REFRESH_EVENT, onRefresh);

    return () => {
      cancelled = true;
      clearInterval(id);
      window.removeEventListener(REFRESH_EVENT, onRefresh);
    };
  }, [interval, enabled]);

  return { data, error, loading };
}
