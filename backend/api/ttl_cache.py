"""Small process-local TTL cache for expensive computed endpoints.

The dashboard/analytics frontend polls several endpoints every 3 seconds.
Most are cheap reads, but impact analysis, cleanup recommendations and
drift prediction resolve from the latest detection and recompute from
scratch on every call. They only change when a new detection or config
lands, so a short TTL gives the same data with a fraction of the compute
— and stops a slow poll from piling threadpool work behind the rest of
the dashboard's requests.
"""

import threading
import time


class TTLCache:
    def __init__(self, ttl_seconds):
        self.ttl_seconds = ttl_seconds
        self._items = {}
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            item = self._items.get(key)
            if item is not None and time.monotonic() - item[0] < self.ttl_seconds:
                return item[1]
            return None

    def set(self, key, value):
        with self._lock:
            self._items[key] = (time.monotonic(), value)

    def clear(self):
        with self._lock:
            self._items.clear()