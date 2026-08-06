import logging
import os
import threading

from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from backend.config import settings

from backend.services.satellite_feed.base import FeedFrame, SatelliteFeed


def _cfg(key, default=None):
    """
    Runtime config value (set via the /config UI) wins, then the
    environment variable, then the default. Non-empty runtime values
    override env so officials can configure live feeds from the UI.
    """

    try:

        from backend.api.config_store import get_config

        value = get_config().get(key)

        if value not in (None, ""):

            return value

    except Exception:

        pass

    return os.getenv(key.upper(), default)


# ----------------------------------------------------------------------
# Render presets: friendly layer name -> (CDSE collection, evalscript).
# Officials can point the feed at a SAR render if their detection model
# was trained on SAR frames instead of optical Sentinel-2.
# ----------------------------------------------------------------------

LAYERS = {
    "TRUE_COLOR": {
        "collection": "sentinel-2-l2a",
        "evalscript": (
            "//VERSION=3\n"
            "function setup() {\n"
            "  return {\n"
            "    input: [\"B04\", \"B03\", \"B02\"],\n"
            "    output: { bands: 3 },\n"
            "  };\n"
            "}\n"
            "function evaluatePixel(sample) {\n"
            "  return [3 * sample.B04, 3 * sample.B03, 3 * sample.B02];\n"
            "}\n"
        ),
    },
    "SAR": {
        "collection": "sentinel-1-grd",
        "evalscript": (
            "//VERSION=3\n"
            "function setup() {\n"
            "  return {\n"
            "    input: [\"VV\", \"VH\"],\n"
            "    output: { bands: 3 },\n"
            "  };\n"
            "}\n"
            "function evaluatePixel(sample) {\n"
            "  const vv = Math.min(1, sample.VV / 0.3);\n"
            "  const vh = Math.min(1, sample.VH / 0.3);\n"
            "  return [vv, vh, vv];\n"
            "}\n"
        ),
    },
}

# Free account: password grant against the CDSE public client.
TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
    "protocol/openid-connect/token"
)

PUBLIC_CLIENT_ID = "cdse-public"

# Sentinel Hub Process API on Copernicus Data Space (no instance id needed).
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"


class SentinelHubFeed(SatelliteFeed):
    """
    Live satellite imagery from Copernicus Data Space (free account).

    Downloads a small tile for the monitored coordinates with the
    Sentinel Hub Process API and serves it as a FeedFrame. Because
    satellite revisit is days rather than seconds, the tile is only
    re-downloaded once per ``frame_cache_ttl_seconds``; the cached
    tile is re-served (same frame_id / path) in between so the
    monitoring loop can recognise and skip it.

    Credentials (env vars or the Config UI):
      - COPERNICUS_USERNAME / COPERNICUS_PASSWORD   (free account)
      - COPERNICUS_CLIENT_ID  / COPERNICUS_CLIENT_SECRET (OAuth client)
    """

    def __init__(self, latitude=None, longitude=None):

        super().__init__()

        self.latitude = float(
            latitude or _cfg("incident_latitude", settings.incident_latitude)
        )

        self.longitude = float(
            longitude or _cfg("incident_longitude", settings.incident_longitude)
        )

        self.token = None

        self.token_expires_at = None

        self.last_fetch_at = None

        self.last_error = None

        self._last_frame = None

        self._token_retry_after = None

        self._lock = threading.Lock()

        self.logger = logging.getLogger(__name__)

    # ----------------------------------------------------------
    # Credentials
    # ----------------------------------------------------------

    @staticmethod
    def _credentials():
        """Return the OAuth form-params for the configured credential set."""

        client_id = _cfg("copernicus_client_id")

        client_secret = _cfg("copernicus_client_secret")

        if client_id and client_secret:

            return {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }

        username = _cfg("copernicus_username")

        password = _cfg("copernicus_password")

        if username and password:

            return {
                "grant_type": "password",
                "client_id": PUBLIC_CLIENT_ID,
                "username": username,
                "password": password,
            }

        return None

    def credentials_configured(self):

        return self._credentials() is not None

    # ----------------------------------------------------------
    # Feed interface
    # ----------------------------------------------------------

    def connect(self):

        if not self.credentials_configured():

            raise RuntimeError(
                "Copernicus Data Space credentials not configured. "
                "Set COPERNICUS_USERNAME/COPERNICUS_PASSWORD (or "
                "COPERNICUS_CLIENT_ID/COPERNICUS_CLIENT_SECRET) in the "
                "Config UI or environment."
            )

        self._connected = True

        return True

    def disconnect(self):

        self._connected = False

    def get_frame(self):

        if not self._connected:

            self.connect()

        if not self.credentials_configured():

            self.last_error = (
                "Copernicus Data Space credentials not configured."
            )

            raise RuntimeError(self.last_error)

        now = datetime.now(timezone.utc)

        cache_ttl = float(_cfg("frame_cache_ttl_seconds", 600))

        # Re-serve the cached tile (same frame) within the TTL.
        if (
            self._last_frame is not None
            and self.last_fetch_at is not None
            and (now - self.last_fetch_at).total_seconds() < cache_ttl
        ):

            self.frames_served += 1

            return self._last_frame

        image_path = self._download_tile(now)

        self._last_frame = FeedFrame(
            frame_id=self.frames_served + 1,
            image_path=image_path,
            latitude=self.latitude,
            longitude=self.longitude,
            timestamp=now,
            source="sentinel_hub",
        )

        self.frames_served += 1

        self.last_fetch_at = now

        self.last_error = None

        return self._last_frame

    def status(self):

        return {
            "source": "sentinel_hub",
            "connected": self._connected,
            "frames_served": self.frames_served,
            "credentials_configured": self.credentials_configured(),
            "token_expires_at": (
                self.token_expires_at.isoformat()
                if self.token_expires_at
                else None
            ),
            "last_fetch_at": (
                self.last_fetch_at.isoformat()
                if self.last_fetch_at
                else None
            ),
            "cache_ttl_seconds": _cfg("frame_cache_ttl_seconds", 600),
            "layer": _cfg("satellite_layer", "TRUE_COLOR"),
            "bbox_span": _cfg("satellite_bbox_span", 0.1),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "error": self.last_error,
        }

    # ----------------------------------------------------------
    # Copernicus Data Space
    # ----------------------------------------------------------

    def _download_tile(self, now):

        token = self._get_token()

        bbox_span = float(_cfg("satellite_bbox_span", 0.1))

        layer = _cfg("satellite_layer", "TRUE_COLOR")

        spec = LAYERS.get(str(layer).upper(), LAYERS["TRUE_COLOR"])

        payload = {
            "input": {
                "bounds": {
                    "bbox": [
                        self.longitude - bbox_span / 2,
                        self.latitude - bbox_span / 2,
                        self.longitude + bbox_span / 2,
                        self.latitude + bbox_span / 2,
                    ],
                    "properties": {
                        "crs": (
                            "http://www.opengis.net/def/crs/"
                            "OGC/1.3/CRS84"
                        )
                    },
                },
                "data": [
                    {
                        "type": spec["collection"],
                        "dataFilter": {"maxCloudCoverage": 50},
                    }
                ],
            },
            "output": {
                "width": 256,
                "height": 256,
                "responses": [
                    {
                        "identifier": "default",
                        "format": {"type": "image/jpeg"},
                    }
                ],
            },
            "evalscript": spec["evalscript"],
        }

        def _request(auth_token):
            return requests.post(
                PROCESS_URL,
                json=payload,
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=60,
            )

        response = _request(token)

        # Token may have expired server-side; refresh once and retry.
        if response.status_code == 401:

            self.token = None

            self.token_expires_at = None

            response = _request(self._get_token(force=True))

        response.raise_for_status()

        out_dir = Path("outputs") / "live_frames"

        out_dir.mkdir(parents=True, exist_ok=True)

        image_path = (
            out_dir
            / f"frame_{now.strftime('%Y%m%dT%H%M%S')}Z.jpg"
        )

        image_path.write_bytes(response.content)

        return str(image_path)

    def _get_token(self, force=False):

        now = datetime.now(timezone.utc)

        with self._lock:

            if (
                not force
                and self.token
                and self.token_expires_at
                and self.token_expires_at > now + timedelta(seconds=60)
            ):

                return self.token

            # Back off after a failure so we don't hammer the token
            # endpoint on every 30s monitoring tick.
            if (
                not force
                and self._token_retry_after
                and now < self._token_retry_after
            ):

                raise RuntimeError(
                    self.last_error or "Copernicus token refresh failed."
                )

            credentials = self._credentials()

            if not credentials:

                self.last_error = (
                    "Copernicus Data Space credentials not configured."
                )

                raise RuntimeError(self.last_error)

            try:

                response = requests.post(
                    TOKEN_URL,
                    data=credentials,
                    timeout=30,
                )

                response.raise_for_status()

                body = response.json()

                self.token = body["access_token"]

                expires_in = int(body.get("expires_in", 3600))

                self.token_expires_at = now + timedelta(
                    seconds=expires_in
                )

                self._token_retry_after = None

                self.last_error = None

                return self.token

            except Exception as exc:

                self.last_error = f"Copernicus token error: {exc}"

                self._token_retry_after = now + timedelta(seconds=60)

                self.token = None

                self.token_expires_at = None

                raise
