import { useSyncExternalStore } from "react";

import { REFRESH_EVENT } from "./useBackendEvents";

/**
 * Poll an async fetcher every `interval` ms, deduplicating concurrent
 * pollers of the same endpoint.
 *
 * Several dashboard cards independently poll the same endpoints —
 * /monitoring/status is fetched by StatsRow, MapPreview and
 * MissionSummary; /ais/suspect-vessels by AISPanel and VesselRanking.
 * Each usePolling() instance used to run its own setInterval + api.get,
 * firing 5 duplicate requests every tick. This hook collapses all
 * consumers that share a `key` into ONE shared store: a single timer
 * and one network fetch per interval, with every subscriber receiving
 * the same result (and only re-rendering when that shared result
 * changes).
 *
 * @param {() => Promise<any>} fetcher - returns fresh data
 * @param {number} interval - poll interval in ms
 * @param {string} key - stable key shared by equivalent pollers
 */
const stores = new Map();

class SharedPollingStore {
  constructor(key, fetcher, interval) {
    this.key = key;
    this.fetcher = fetcher;
    this.interval = interval;
    // A stable snapshot reference: useSyncExternalStore requires
    // getSnapshot to return the same object until the data changes.
    this.state = { data: undefined, error: null, loading: true };
    this.listeners = new Set();
    this.timer = null;
    this.started = false;
  }

  subscribe = (listener) => {
    this.listeners.add(listener);

    // First consumer starts the poller; later ones just join in.
    if (!this.started) {
      this.started = true;
      this.run();
      this.timer = setInterval(() => this.run(), this.interval);
      window.addEventListener(REFRESH_EVENT, this.refresh);
    }

    return () => {
      this.listeners.delete(listener);

      // Stop the timer once the last consumer unmounts so a hidden
      // page never keeps polling in the background.
      if (this.listeners.size === 0 && this.timer != null) {
        clearInterval(this.timer);
        this.timer = null;
        this.started = false;
        window.removeEventListener(REFRESH_EVENT, this.refresh);
      }
    };
  };

  getSnapshot = () => this.state;

  getServerSnapshot = () => this.state;

  setState(state) {
    this.state = state;
    this.listeners.forEach((listener) => listener());
  }

  run = async () => {
    try {
      const data = await this.fetcher();
      this.setState({ data, error: null, loading: false });
    } catch (err) {
      // Keep any previously loaded data on a transient failure so the
      // card doesn't flash empty on a single dropped request.
      this.setState({ data: this.state.data, error: err, loading: false });
    }
  };

  // Refetch immediately when the backend signals a new detection or
  // (re)start, matching usePolling's REFRESH_EVENT behaviour.
  refresh = () => {
    if (this.started) this.run();
  };
}

function getStore(key, fetcher, interval) {
  let store = stores.get(key);
  if (!store) {
    store = new SharedPollingStore(key, fetcher, interval);
    stores.set(key, store);
  }
  return store;
}

export function useSharedPolling(fetcher, interval, key) {
  const store = getStore(key, fetcher, interval);
  return useSyncExternalStore(
    store.subscribe,
    store.getSnapshot,
    store.getServerSnapshot,
  );
}
