"""
API package initialization with versioned routes.
"""

from backend.api.auth import router as auth_router
from backend.api.users import router as users_router
from backend.api.incidents import router as incidents_router
from backend.api.monitoring import router as monitoring_router
from backend.api.weather import router as weather_router
from backend.api.alerts import router as alerts_router
from backend.api.system import router as system_router
from backend.api.drift import router as drift_router
from backend.api.report import router as report_router
from backend.api.config import router as config_router
from backend.api.errors import router as error_router
from backend.api.cleanup import router as cleanup_router
from backend.api.detection import router as detection_router
from backend.api.impact import router as impact_router
from backend.api.ais import router as ais_router


def get_v1_routers():
    """Return all v1 routers for versioned API."""
    return [
        (auth_router, "/auth", ["Authentication"]),
        (users_router, "/users", ["Users"]),
        (incidents_router, "/incidents", ["Incidents"]),
        (monitoring_router, "/monitoring", ["Monitoring"]),
        (weather_router, "/weather", ["Weather"]),
        (alerts_router, "/alerts", ["Alerts"]),
        (system_router, "/system", ["System"]),
        (drift_router, "/drift", ["Drift Prediction"]),
        (report_router, "/reports", ["Reports"]),
        (config_router, "/config", ["Configuration"]),
        (cleanup_router, "/cleanup", ["Cleanup"]),
        (detection_router, "/detection", ["Detection"]),
        (impact_router, "/impact", ["Impact Analysis"]),
        (ais_router, "/ais", ["AIS Analysis"]),
        (error_router, "/errors", ["Errors"]),
    ]