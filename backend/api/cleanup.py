from fastapi import APIRouter

from backend.services.cleanup_recommender import (
    CleanupRecommendationEngine,
    CleanupInput,
)

from backend.api.context import (
    incident_location,
    incident_spill_area,
    latest_incident,
)

router = APIRouter(
    prefix="/cleanup",
    tags=["Cleanup Recommendation"],
)


@router.get("/recommend")
def recommend(
    spill_area: float = None,
    distance_to_coast: float = None,
    risk_level: str = None,
    wind_speed: float = None,
    current_speed: float = None,
):

    incident = latest_incident()

    latitude, longitude = incident_location()

    # -----------------------------
    # Resolve defaults from the latest incident
    # -----------------------------

    if spill_area is None:

        spill_area = (
            incident.get("spill_area_km2")
            if incident
            else incident_spill_area()
        )

    if risk_level is None:

        risk_level = (
            incident.get("risk_level")
            if incident
            else "LOW"
        )

    if distance_to_coast is None:

        env = (
            incident.get("impact", {}).get("environmental", {})
            if incident
            else {}
        )

        distance_to_coast = (
            env.get("Nearest Coastline", {}).get("distance", 10.0)
        )

    if wind_speed is None:

        weather = (
            incident.get("weather", {})
            if incident
            else {}
        )

        wind_speed = weather.get("wind_speed", 0)

    if current_speed is None:

        current_speed = (
            incident.get("current_speed", 0.0)
            if incident
            else 0.0
        )

    data = CleanupInput(
        spill_area=spill_area,
        distance_to_coast=distance_to_coast,
        risk_level=risk_level,
        wind_speed=wind_speed,
        current_speed=current_speed,
    )

    engine = CleanupRecommendationEngine()

    return engine.recommend(data)
