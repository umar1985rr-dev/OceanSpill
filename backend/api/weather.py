from fastapi import APIRouter

from backend.services.drift_prediction.data_loader import (
    EnvironmentalDataLoader,
)

from backend.api.context import incident_location

router = APIRouter(
    prefix="/weather",
    tags=["Weather"],
)

loader = EnvironmentalDataLoader()


@router.get("/current")
def current(lat: float = None, lon: float = None):

    latitude, longitude = incident_location()

    if lat is not None:

        latitude = lat

    if lon is not None:

        longitude = lon

    weather = loader.load_live_weather(
        latitude,
        longitude,
    )

    current_row = loader.get_nearest_current(
        latitude,
        longitude,
    )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "wind_speed_kmh": weather["wind_speed"],
        "wind_direction_deg": weather["wind_direction"],
        "current_speed": float(current_row["current_speed"]),
        "current_direction": float(current_row["current_direction"]),
    }
