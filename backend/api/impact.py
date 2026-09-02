from datetime import datetime

from fastapi import APIRouter

from backend.services.impact_analysis import (
    EnvironmentalImpactAnalyzer,
    EconomicImpactAnalyzer,
    RiskScoringEngine,
    ImpactDashboard,
    ImpactInput,
)

from backend.api.context import incident_location, incident_spill_area
from backend.api.ttl_cache import TTLCache

router = APIRouter(
    prefix="/impact",
    tags=["Impact Analysis"],
)

environment = EnvironmentalImpactAnalyzer()

economic = EconomicImpactAnalyzer()

risk_engine = RiskScoringEngine()

dashboard = ImpactDashboard()

# /dashboard and /summary run the same full analysis on every 3s poll.
# It only changes when a new detection (lat/lon/area) or config lands, so
# cache the result for a few seconds instead of recomputing it 2x per poll.
_dashboard_cache = TTLCache(ttl_seconds=10)


def _dashboard_result(impact):
    """generate() with a short TTL keyed on the resolved incident inputs."""
    key = (
        round(impact.latitude, 6),
        round(impact.longitude, 6),
        round(impact.spill_area, 6),
    )
    cached = _dashboard_cache.get(key)
    if cached is not None:
        return cached
    result = dashboard.generate(impact)
    _dashboard_cache.set(key, result)
    return result


def build_input(lat, lon, spill_area):

    latitude, longitude = incident_location()

    if lat is not None:

        latitude = lat

    if lon is not None:

        longitude = lon

    area = (
        spill_area
        if spill_area is not None
        else incident_spill_area()
    )

    return ImpactInput(
        latitude=latitude,
        longitude=longitude,
        spill_area=area,
        predicted_path=[],
        risk_zones=[],
        timestamp=datetime.now(),
    )


@router.get("/environment")
def environment_report(lat: float = None, lon: float = None, spill_area: float = None):

    impact = build_input(lat, lon, spill_area)

    return environment.analyze(impact)


@router.get("/economic")
def economic_report(lat: float = None, lon: float = None, spill_area: float = None):

    impact = build_input(lat, lon, spill_area)

    return economic.analyze(impact)


@router.get("/risk")
def risk_report(lat: float = None, lon: float = None, spill_area: float = None):

    impact = build_input(lat, lon, spill_area)

    return risk_engine.calculate(impact)


@router.get("/dashboard")
def dashboard_report(lat: float = None, lon: float = None, spill_area: float = None):

    impact = build_input(lat, lon, spill_area)

    return _dashboard_result(impact)


@router.get("/summary")
def summary(lat: float = None, lon: float = None, spill_area: float = None):

    impact = build_input(lat, lon, spill_area)

    return _dashboard_result(impact)
