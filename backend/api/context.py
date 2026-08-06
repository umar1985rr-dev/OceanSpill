from backend.config import settings

from backend.services.monitoring import monitoring_service


def incident_location():
    """
    Resolve the spill coordinates for API calls.

    Priority: latest detected incident, then the current live
    frame, then the configured default location.
    """

    state = monitoring_service.state.to_dict()

    last = state.get("last_detection")

    if last:

        return last["latitude"], last["longitude"]

    frame = state.get("current_frame")

    if frame:

        return frame["latitude"], frame["longitude"]

    try:
        from backend.api.config_store import get as _get_cfg
        return _get_cfg("incident_latitude", settings.incident_latitude), _get_cfg("incident_longitude", settings.incident_longitude)
    except Exception:
        return settings.incident_latitude, settings.incident_longitude


def incident_spill_area(default=2.0):
    """
    Resolve the spill area (km²) for API calls.
    """

    state = monitoring_service.state.to_dict()

    last = state.get("last_detection")

    if last and last.get("spill_area_km2"):

        return last["spill_area_km2"]

    return default


def latest_incident():
    """
    Return the most recent incident dict, or None.
    """

    state = monitoring_service.state.to_dict()

    incidents = state.get("incidents", [])

    if incidents:

        return incidents[-1]

    return None
