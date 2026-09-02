import math

from datetime import datetime

from fastapi import APIRouter

from backend.services.ais_analysis.models import SpillLocation

from backend.services.ais_analysis.nearby import NearbyVesselFinder

from backend.services.ais_analysis.movement import MovementAnalyzer

from backend.services.ais_analysis.ranking import SuspectRanker

from backend.services.monitoring.service import _load_ais_dataframe

from backend.api.context import incident_location

router = APIRouter(
    prefix="/ais",
    tags=["AIS Vessel Analysis"],
)


def _clean(value):
    """
    Convert a pandas/numpy scalar into a plain JSON-friendly value.
    """

    if hasattr(value, "item"):

        value = value.item()

    if isinstance(value, float):

        if math.isnan(value) or math.isinf(value):

            return None

    return value


def _row_to_dict(row):
    """
    Convert a pandas Series (one vessel) into plain JSON values.
    """

    result = {}

    for key, value in row.items():

        result[key] = _clean(value)

    return result


def _resolve_spill(lat, lon):

    latitude, longitude = incident_location()

    if lat is not None:

        latitude = lat

    if lon is not None:

        longitude = lon

    return SpillLocation(
        latitude=latitude,
        longitude=longitude,
        timestamp=datetime.now(),
    )


@router.get("/health")
def health():

    return {
        "status": "AIS Module Ready",
        "module": "AIS Analysis",
    }


@router.get("/nearby-vessels")
def nearby_vessels(lat: float = None, lon: float = None, radius: float = 20.0):

    spill = _resolve_spill(lat, lon)

    dataframe = _load_ais_dataframe()

    nearby = NearbyVesselFinder().find_nearby(
        dataframe,
        spill,
        radius_km=radius,
    )

    vessels = [
        _row_to_dict(row)
        for _, row in nearby.head(50).iterrows()
    ]

    return {
        "latitude": spill.latitude,
        "longitude": spill.longitude,
        "radius_km": radius,
        "count": len(nearby),
        "vessels": vessels,
    }


@router.get("/movement-analysis")
def movement_analysis(lat: float = None, lon: float = None, radius: float = 20.0):

    spill = _resolve_spill(lat, lon)

    dataframe = _load_ais_dataframe()

    nearby = NearbyVesselFinder().find_nearby(
        dataframe,
        spill,
        radius_km=radius,
    )

    analyzed = MovementAnalyzer().analyze(nearby)

    vessels = [
        _row_to_dict(row)
        for _, row in analyzed.head(50).iterrows()
    ]

    return {
        "latitude": spill.latitude,
        "longitude": spill.longitude,
        "algorithm": "Movement Score",
        "count": len(analyzed),
        "vessels": vessels,
    }


@router.get("/suspect-vessels")
def suspect_vessels(lat: float = None, lon: float = None, radius: float = 20.0):

    spill = _resolve_spill(lat, lon)

    dataframe = _load_ais_dataframe()

    nearby = NearbyVesselFinder().find_nearby(
        dataframe,
        spill,
        radius_km=radius,
    )

    analyzed = MovementAnalyzer().analyze(nearby)

    ranked = SuspectRanker().rank(analyzed)

    vessels = [
        _row_to_dict(row)
        for _, row in ranked.head(10).iterrows()
    ]

    return {
        "latitude": spill.latitude,
        "longitude": spill.longitude,
        "algorithm": "Suspect Score",
        "count": len(ranked),
        "vessels": vessels,
    }


@router.get("/map")
def map_status(lat: float = None, lon: float = None):

    spill = _resolve_spill(lat, lon)

    dataframe = _load_ais_dataframe()

    nearby = NearbyVesselFinder().find_nearby(
        dataframe,
        spill,
        radius_km=20,
    )

    analyzed = MovementAnalyzer().analyze(nearby)

    ranked = SuspectRanker().rank(analyzed)

    map_path = None

    if not ranked.empty:

        from backend.services.ais_analysis.visualization import (
            AISMapVisualizer,
        )

        map_path = AISMapVisualizer().create_map(
            spill,
            ranked,
        )

    return {
        "latitude": spill.latitude,
        "longitude": spill.longitude,
        "map_path": str(map_path) if map_path else None,
        "vessels_ranked": len(ranked),
    }
