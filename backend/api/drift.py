from datetime import datetime

from fastapi import APIRouter

from backend.services.drift_prediction.predictor import DriftPredictor

from backend.services.drift_prediction.models import SpillData

from backend.services.drift_prediction.visualization import DriftMap

from backend.api.context import incident_location, incident_spill_area
from backend.api.ttl_cache import TTLCache

# Drift forecast only changes when the incident moves or hours changes.
# Cache the prediction per resolved location + hours so repeated polls
# (overlay, trajectory, animated panels hitting the same endpoint every
# 3s) hit cache after the first fetch of each window.
_drift_pred_cache = TTLCache(ttl_seconds=10)

router = APIRouter(
    prefix="/drift",
    tags=["Drift Prediction"],
)


def _predict(lat, lon, hours):

    latitude, longitude = incident_location()

    if lat is not None:

        latitude = lat

    if lon is not None:

        longitude = lon

    area = incident_spill_area()
    key = (round(latitude, 6), round(longitude, 6), round(area, 6), int(hours))
    cached = _drift_pred_cache.get(key)
    if cached is not None:
        return cached

    spill = SpillData(
        latitude=latitude,
        longitude=longitude,
        area=area,
        timestamp=datetime.now(),
    )

    predictor = DriftPredictor()

    predictions = predictor.predict(
        spill,
        hours=hours,
    )

    result = (spill, predictions)
    _drift_pred_cache.set(key, result)
    return result


@router.get("/health")
def health():

    return {
        "status": "Drift Prediction Ready",
        "module": "Spill Drift Prediction",
    }


@router.get("/predict")
def predict(lat: float = None, lon: float = None, hours: int = 24):

    try:

        spill, predictions = _predict(lat, lon, hours)

        return {
            "latitude": spill.latitude,
            "longitude": spill.longitude,
            "prediction_hours": hours,
            "count": len(predictions),
            "predictions": predictions,
        }

    except Exception as exc:

        return {
            "latitude": lat,
            "longitude": lon,
            "predictions": [],
            "error": str(exc),
        }


@router.get("/path")
def path(lat: float = None, lon: float = None, hours: int = 24):

    spill, predictions = _predict(lat, lon, hours)

    return {
        "latitude": spill.latitude,
        "longitude": spill.longitude,
        "path": predictions,
    }


@router.get("/risk-zones")
def risk_zones(lat: float = None, lon: float = None, hours: int = 24):

    spill, predictions = _predict(lat, lon, hours)

    zones = []

    for point in predictions:

        zones.append(
            {
                "hour": point["hour"],
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "radius_m": 1250,
            }
        )

    return {
        "latitude": spill.latitude,
        "longitude": spill.longitude,
        "count": len(zones),
        "zones": zones,
    }


@router.get("/map")
def drift_map(lat: float = None, lon: float = None, hours: int = 24):

    spill, predictions = _predict(lat, lon, hours)

    map_path = DriftMap().create(
        spill,
        predictions,
        risk_zones=[],
    )

    return {
        "map_path": str(map_path),
        "points": len(predictions),
    }
