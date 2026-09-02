import json
import threading

from datetime import datetime
from pathlib import Path

STATE_PATH = Path("monitoring_state.json")


def _iso(dt):

    if dt is None:

        return None

    return dt.isoformat()


class MonitoringState:
    """
    Thread-safe, persisted store for the live monitoring loop.

    Holds feed status, the current frame, the latest detection and
    the full incident history. Persists to JSON so state survives
    a restart.
    """

    def __init__(self, state_path=STATE_PATH):

        self._lock = threading.Lock()

        self.state_path = Path(state_path)

        self.data = {

            "feed_status": {},

            "last_checked_at": None,

            "current_frame": None,

            "last_detection": None,

            "incidents": [],

            "alerts": [],

            "is_running": False,

            "is_processing": False,

            "report_path": None,

            # Monotonic event counter: bumped on monitoring start/stop and on
            # every new detection. Lets clients detect "something happened"
            # and refresh immediately.
            "version": 0,

        }

        self._load()

    # ----------------------------------------------------------
    # Setters
    # ----------------------------------------------------------

    def set_feed_status(self, status):

        with self._lock:

            self.data["feed_status"] = status

            self._save()

    def set_current_frame(self, frame_dict):

        with self._lock:

            self.data["current_frame"] = frame_dict

            self._save()

    def set_last_checked(self, dt):

        with self._lock:

            self.data["last_checked_at"] = _iso(dt)

            self._save()

    def set_last_detection(self, incident):

        with self._lock:

            self.data["last_detection"] = incident

            self._save()

    def add_incident(self, incident):

        with self._lock:

            self.data["incidents"].append(incident)

            self.data["report_path"] = incident.get("report_path")

            self._save()

    def add_alert(self, alert):

        with self._lock:

            self.data["alerts"].append(alert)

            self._save()

    def set_running(self, value):

        with self._lock:

            self.data["is_running"] = bool(value)

            self._save()

    def set_processing(self, value):

        with self._lock:

            self.data["is_processing"] = bool(value)

            self._save()

    def bump_version(self):

        """
        Increment the event version counter and persist.

        Used by the monitoring loop whenever something the UI should
        react to happens (a new detection, monitoring start/stop).
        """

        with self._lock:

            self.data["version"] = int(self.data.get("version", 0)) + 1

            self._save()

            return self.data["version"]

    # ----------------------------------------------------------
    # Readers
    # ----------------------------------------------------------

    def to_dict(self):

        with self._lock:

            return json.loads(json.dumps(self.data))

    def latest_incident(self):

        with self._lock:

            if self.data["incidents"]:

                return self.data["incidents"][-1]

            return None

    # ----------------------------------------------------------
    # Persistence
    # ----------------------------------------------------------

    def _save(self):

        try:

            self.state_path.write_text(
                json.dumps(self.data, indent=2),
                encoding="utf-8",
            )

        except OSError:

            pass

    def _load(self):

        if not self.state_path.exists():

            return

        try:

            saved = json.loads(
                self.state_path.read_text(encoding="utf-8")
            )

            self.data.update(saved)

        except (OSError, ValueError):

            pass

        # `is_processing` is a transient in-process lock — a stale
        # True from a killed/restarted process would permanently skip
        # every tick, so it never survives a reload.
        self.data["is_processing"] = False
