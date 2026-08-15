import abc
import logging
import math
import os
import threading
import time

from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

from backend.config import settings
from backend.services.ais_analysis.validator import AISValidator


def _cfg(key, default=None):

    """Runtime config (set via the /config UI) wins, then env, then default."""

    try:

        from backend.api.config_store import get_config

        value = get_config().get(key)

        if value not in (None, ""):

            return value

    except Exception:

        pass

    return os.getenv(key.upper(), default)


# Anchor for dataset paths so we can find the default AIS CSV no matter
# which directory the backend is started from.
REPO_ROOT = Path(__file__).resolve().parents[3]


class AISSource(abc.ABC):

    """
    Pluggable AIS data provider.

    Implementations return a DataFrame whose columns satisfy
    ``AISValidator.REQUIRED_COLUMNS`` so the existing ranking
    pipeline (NearbyVesselFinder / MovementAnalyzer / SuspectRanker)
    works unchanged regardless of where the positions came from.
    """

    @property
    def source_name(self) -> str:

        return "unknown"

    @property
    def refreshes(self) -> bool:

        """
        True when the source should be re-fetched periodically
        (live API), False when the underlying data is a static file
        that changes only on explicit upload.
        """

        return False

    @abc.abstractmethod
    def fetch(self, force=False) -> pd.DataFrame:

        """
        Return the AIS DataFrame.

        The caller handles caching / TTL. ``force=True`` forces a
        fresh fetch (e.g. after a new file upload).
        """

        raise NotImplementedError


# ======================================================================
# CSV source (the default — wraps the existing loader)
# ======================================================================


class CsvSource(AISSource):

    source_name = "csv"

    def __init__(self):

        self._df = None

    def fetch(self, force=False) -> pd.DataFrame:

        if self._df is not None and not force:

            return self._df

        # Re-read every time so a new upload takes effect.
        from backend.services.ais_analysis.loader import AISLoader

        self._df = AISLoader().load()

        return self._df


# ======================================================================
# Simulated Live — animates the uploaded CSV for demo purposes
# ======================================================================


class SimulatedLiveSource(AISSource):

    source_name = "simulated_live"

    refreshes = True

    def __init__(self):

        self._base = None

        self._epoch = time.monotonic()

        self._last_positions = None

        self.logger = logging.getLogger(__name__)

    def _load_base(self):

        if self._base is not None:

            return

        from backend.services.ais_analysis.loader import AISLoader

        raw = AISLoader().load()

        # Parse timestamps and keep the latest position per MMSI so
        # the "fleet" is a realistic set of distinct vessels.

        raw["_ts"] = pd.to_datetime(raw["BaseDateTime"], errors="coerce")

        self._base = (
            raw.dropna(subset=["_ts"])
            .sort_values("_ts")
            .groupby("MMSI")
            .tail(1)
            .copy()
            .reset_index(drop=True)
        )

        self._base = self._base.astype(
            {
                "LAT": float,
                "LON": float,
                "SOG": float,
                "COG": float,
            }
        )

    def fetch(self, force=False) -> pd.DataFrame:

        self._load_base()

        now = time.monotonic()

        elapsed_h = (now - self._epoch) / 3600.0

        df = self._base.copy()

        # Advance each vessel by SOG × COG for the elapsed time.
        sog = df["SOG"].fillna(0)

        cog = df["COG"].fillna(0)

        dist_km = sog * 1.852 * elapsed_h

        dx = dist_km * pd.Series(
            [math.sin(math.radians(c)) for c in cog], index=df.index
        )

        dy = dist_km * pd.Series(
            [math.cos(math.radians(c)) for c in cog], index=df.index
        )

        new_lat = df["LAT"] + dy / 111.0

        cos_lat = new_lat.apply(
            lambda lat: math.cos(math.radians(lat)) or 1e-6
        )

        new_lon = df["LON"] + dx / (111.0 * cos_lat)

        df["LAT"] = new_lat

        df["LON"] = new_lon

        # Update BaseDateTime to reflect the moved timestamp.
        df["BaseDateTime"] = (
            df["_ts"] + timedelta(seconds=elapsed_h * 3600)
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

        return df.drop(columns=["_ts"])


# ======================================================================
# AISHub — free registration, HTTP CSV endpoint
# ======================================================================


class AISHubSource(AISSource):

    """
    Fetch live positions from the free AISHub service.

    Requires a registered account (https://data.aishub.net/).
    Set AISHUB_USERNAME and AISHUB_API_KEY via env or the Config UI.
    """

    source_name = "aishub"

    refreshes = True

    ENDPOINT = "https://data.aishub.net/ws.php"

    def __init__(self):

        self.logger = logging.getLogger(__name__)

    def fetch(self, force=False) -> pd.DataFrame:

        username = _cfg("aishub_username")

        api_key = _cfg("aishub_api_key")

        if not username or not api_key:

            raise RuntimeError(
                "AISHub credentials not configured. "
                "Set AISHUB_USERNAME and AISHUB_API_KEY via the "
                "Config UI or environment."
            )

        # Incident coordinates (bounding-box around them).
        lat = float(_cfg("incident_latitude", settings.incident_latitude))

        lon = float(_cfg("incident_longitude", settings.incident_longitude))

        bbox_span = float(_cfg("ais_bbox_span", 2.0))

        params = {
            "username": username,
            "apikey": api_key,
            "format": 1,  # 1 = CSV
            "output": "csv",
            "compress": 0,
        }

        response = requests.get(
            self.ENDPOINT,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        df = pd.read_csv(StringIO(response.text))

        # AISHub columns differ from ours; map them.
        RENAME = {
            "MMSI": "MMSI",
            "TIME": "BaseDateTime",
            "LATITUDE": "LAT",
            "LONGITUDE": "LON",
            "COG": "COG",
            "SOG": "SOG",
            "HDG": "Heading",
            "NAVSTAT": "NAVSTAT",
            "IMO": "IMO",
            "NAME": "VesselName",
            "TYPE": "VesselType",
        }

        df = df.rename(columns=RENAME)

        # Filter to bounding box.
        df = df[
            (df["LAT"] >= lat - bbox_span / 2)
            & (df["LAT"] <= lat + bbox_span / 2)
            & (df["LON"] >= lon - bbox_span / 2)
            & (df["LON"] <= lon + bbox_span / 2)
        ]

        AISValidator.validate(df)

        return df


# ======================================================================
# MarineTraffic — paid API (best-effort, needs API key)
# ======================================================================


class MarineTrafficSource(AISSource):

    """
    Fetch live positions from MarineTraffic / Kpler v3 API.

    Requires a subscription key (services.marinetraffic.com or kpler.com).
    Set MARINE_TRAFFIC_API_KEY via env or the Config UI.
    """

    source_name = "marinetraffic"

    refreshes = True

    # The exact endpoint may shift as MarineTraffic migrates to Kpler.
    # If it doesn't work, check your account docs and update BASE_URL.
    BASE_URL = "https://services.marinetraffic.com/api/v3/ships"

    def __init__(self):

        self.logger = logging.getLogger(__name__)

    def fetch(self, force=False) -> pd.DataFrame:

        api_key = _cfg("marine_traffic_api_key")

        if not api_key:

            raise RuntimeError(
                "MarineTraffic API key not configured. "
                "Set MARINE_TRAFFIC_API_KEY via the Config UI "
                "or environment."
            )

        lat = float(_cfg("incident_latitude", settings.incident_latitude))

        lon = float(_cfg("incident_longitude", settings.incident_longitude))

        bbox_span = float(_cfg("ais_bbox_span", 2.0))

        params = {
            "apikey": api_key,
            "minlat": lat - bbox_span / 2,
            "maxlat": lat + bbox_span / 2,
            "minlon": lon - bbox_span / 2,
            "maxlon": lon + bbox_span / 2,
            "msgtype": "extended",
            "protocol": "jsono",
        }

        response = requests.get(self.BASE_URL, params=params, timeout=30)

        response.raise_for_status()

        payload = response.json()

        records = payload.get("data", payload) if isinstance(payload, dict) else payload

        df = pd.DataFrame(records)

        RENAME = {
            "MMSI": "MMSI",
            "LAT": "LAT",
            "LON": "LON",
            "SO": "SOG",
            "CO": "COG",
            "HEADING": "Heading",
            "IMO": "IMO",
            "SHIPNAME": "VesselName",
            "SHIPTYPE": "VesselType",
            "LAST_POS": "BaseDateTime",
        }

        df = df.rename(columns=RENAME)

        AISValidator.validate(df)

        return df


# ======================================================================
# Global provider manager — thread-safe, TTL-cached
# ======================================================================


_lock = threading.Lock()

_cache = {
    "source_key": None,
    "dataframe": None,
    "fetched_at": None,
}

_SOURCE_MAP = {
    "csv": CsvSource,
    "simulated_live": SimulatedLiveSource,
    "aishub": AISHubSource,
    "marinetraffic": MarineTrafficSource,
}


def get_ais_data(force=False, source_type=None) -> pd.DataFrame:
    """
    Return the current AIS dataframe using the source configured in
    ``ais_source`` (runtime config), or an explicit *source_type*
    override (used by the /config/test endpoint). The data is cached
    in-memory and refreshed only when the source changes, the TTL
    expires (for live sources), or ``force=True`` is passed (e.g.
    after a new CSV upload).

    Thread-safe; called from the monitoring loop and from ``/ais/*``
    endpoints in parallel.
    """

    global _cache

    source_name = source_type or _cfg("ais_source", "csv")

    ttl = float(_cfg("ais_refresh_interval_seconds", 300))

    now = time.monotonic()

    with _lock:

        stale = (
            _cache["fetched_at"] is None
            or (now - _cache["fetched_at"]) > ttl
        )

        source_changed = _cache["source_key"] != source_name

        cls = _SOURCE_MAP.get(source_name)

        if cls is None:

            raise ValueError(
                f"Unknown AIS source '{source_name}'. "
                f"Supported: {', '.join(sorted(_SOURCE_MAP))}"
            )

        source = cls()

        needs_refresh = force or source_changed or (source.refreshes and stale)

        if not needs_refresh and _cache["dataframe"] is not None:

            return _cache["dataframe"]

        df = source.fetch(force=force or source_changed)

        _cache = {
            "source_key": source_name,
            "dataframe": df,
            "fetched_at": now,
        }

        return df
