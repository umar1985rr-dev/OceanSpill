from pathlib import Path
import math
import time

import pandas as pd
import requests


# Anchor for dataset paths so the loader works no matter which directory
# the backend is started from. data_loader.py -> drift_prediction ->
# services -> backend -> root.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Ocean current data must be uploaded by the user.  The file lands in
# dataset/raw/geographic/ocean_currents.csv (see upload route).
GEO_UPLOAD_DIR = REPO_ROOT / "dataset" / "raw" / "geographic"
UPLOADED_CURRENT_PATH = GEO_UPLOAD_DIR / "ocean_currents.csv"

# Live weather comes from an external API (Open-Meteo) and is slow
# (seconds when it responds, up to timeout when it doesn't). The frontend
# polls every 3s, so cache the response for several minutes: one external
# call per window instead of dozens, and a stall no longer freezes the
# dashboard.
_WEATHER_TTL_SECONDS = 300

_weather_cache = {}          # (lat, lon) -> (fetched_at, payload or None)
_current_df_cache = {"key": None, "df": None}  # ("mtime-path", DataFrame)


class EnvironmentalDataLoader:
    def get_nearest_current(
        self,
        latitude,
        longitude,
    ):

        currents = self.load_ocean_currents()

        nearest = None
        minimum_distance = float("inf")

        for _, row in currents.iterrows():

            distance = math.sqrt(
                (latitude - row["latitude"]) ** 2 +
                (longitude - row["longitude"]) ** 2
            )

            if distance < minimum_distance:
                minimum_distance = distance
                nearest = row

        return nearest

    def __init__(self):

        self.current_path = UPLOADED_CURRENT_PATH

    def _resolve_current_path(self):
        """
        Pick the ocean-currents file to read.

        Uploads land at dataset/raw/geographic/ocean_currents.csv (a
        re-upload overwrites it, so a new file takes effect immediately).
        """
        if UPLOADED_CURRENT_PATH.exists():
            return UPLOADED_CURRENT_PATH
        raise FileNotFoundError(
            "No ocean current data found. Upload ocean_currents.csv "
            "via the Configuration page or place it at "
            "dataset/raw/geographic/ocean_currents.csv."
        )

    def load_ocean_currents(self):

        path = self._resolve_current_path()

        # Cache the parsed DataFrame; re-read when the chosen file
        # changes (fresh upload → new name or new mtime).
        cache_key = f"{path}-{path.stat().st_mtime_ns}"

        if _current_df_cache["key"] != cache_key:
            if not path.exists():
                raise FileNotFoundError(
                    f"Ocean current file not found: {path}"
                )

            df = pd.read_csv(path)

            required = [
                "latitude",
                "longitude",
                "current_speed",
                "current_direction",
            ]

            for column in required:
                if column not in df.columns:
                    raise ValueError(
                        f"Missing column: {column}"
                    )

            _current_df_cache["key"] = cache_key
            _current_df_cache["df"] = df

        return _current_df_cache["df"]

    def load_live_weather(
        self,
        latitude,
        longitude,
    ):

        key = (round(float(latitude), 4), round(float(longitude), 4))
        now = time.monotonic()

        cached = _weather_cache.get(key)
        if cached is not None and now - cached[0] < _WEATHER_TTL_SECONDS and cached[1] is not None:
            return cached[1]

        try:
            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={latitude}"
                f"&longitude={longitude}"
                "&current=wind_speed_10m,wind_direction_10m"
            )

            response = requests.get(
                url,
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()["current"]

            payload = {
                "wind_speed": data["wind_speed_10m"],
                "wind_direction": data["wind_direction_10m"],
            }
        except Exception:
            # Open-Meteo is down or slow. Serve the last good value if we
            # have one (stale-but-working), otherwise surface the error.
            if cached is not None and cached[1] is not None:
                return cached[1]
            raise

        _weather_cache[key] = (now, payload)
        return payload