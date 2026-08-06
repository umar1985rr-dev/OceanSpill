"""
Runtime configuration store.

Allows officials to update model inputs (coordinates, thresholds,
data file paths) through the UI without restarting the backend.

Settings persist to a JSON file next to the repo root so they
survive restarts.  All fields are optional — missing values fall
back to the defaults already in backend.config.settings.
"""

import json
import threading
from pathlib import Path

from backend.config import settings

CONFIG_PATH = Path("runtime_config.json")

_lock = threading.Lock()

_defaults = {
    "incident_latitude": settings.incident_latitude,
    "incident_longitude": settings.incident_longitude,
    "detection_threshold": settings.detection_threshold,
    "monitor_interval_seconds": settings.monitor_interval_seconds,
    "feed_source": settings.feed_source,
    "simulator_images_dir": settings.simulator_images_dir,
    "ais_csv_path": "dataset/raw/ais_data/ais_data.csv",
    "copernicus_username": "",
    "copernicus_password": "",
    "copernicus_client_id": "",
    "copernicus_client_secret": "",
    "satellite_layer": "TRUE_COLOR",
    "frame_cache_ttl_seconds": 600,
    "satellite_bbox_span": 0.1,
    "ais_source": "csv",
    "ais_refresh_interval_seconds": 300,
    "marine_traffic_api_key": "",
    "aishub_username": "",
    "aishub_api_key": "",
    "ais_bbox_span": 2.0,
}


def _load():
    """Load persisted config, merging with env-var defaults."""
    data = dict(_defaults)
    if CONFIG_PATH.exists():
        try:
            data.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    return data


def _save(data):
    CONFIG_PATH.write_text(
        json.dumps(data, indent=2, default=str),
        encoding="utf-8",
    )


# Module-level cache so the first read is fast.
_cache = _load()


def get_config():
    """Return a copy of the current runtime config."""
    with _lock:
        return dict(_cache)


def update_config(patch: dict):
    """
    Merge *patch* into the runtime config, persist, and return
    the full updated config.

    Unknown keys are ignored so callers can safely pass the whole
    form payload.
    """
    global _cache
    with _lock:
        for key in _defaults:
            if key in patch:
                _cache[key] = patch[key]
        _save(_cache)
        return dict(_cache)


def get(key, default=None):
    with _lock:
        return _cache.get(key, default)
