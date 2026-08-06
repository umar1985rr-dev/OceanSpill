import math

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.config import settings

from backend.services.report_generator import (
    ReportGenerator,
    IncidentReport,
)

from backend.api.context import latest_incident

router = APIRouter(
    prefix="/report",
    tags=["Report Generator"],
)

REPORT_PATH = Path("reports") / "OceanSpill_AI_Incident_Report.pdf"


def _direction(delta_lat, delta_lon):

    angle = math.degrees(
        math.atan2(delta_lon, delta_lat)
    )

    directions = [
        "N", "NE", "E", "SE", "S", "SW", "W", "NW",
    ]

    index = int(((angle + 360) % 360) / 45) % 8

    return directions[index]


def _drift_summary(drift):

    if not drift:

        return {
            "Direction": "N/A",
            "Estimated Drift": "N/A",
            "Time": "N/A",
        }

    first = drift[0]

    last = drift[-1]

    return {
        "Direction": _direction(
            last["latitude"] - first["latitude"],
            last["longitude"] - first["longitude"],
        ),
        "Estimated Drift": f"{len(drift)} hourly steps",
        "Time": f"{last['hour']} Hours",
    }


def _report_from_incident(incident):

    env_report = (
        incident.get("impact", {}).get("environmental", {})
        or {}
    )

    eco_report = (
        incident.get("impact", {}).get("economic", {})
        or {}
    )

    weather = incident.get("weather", {}) or {}

    return IncidentReport(
        project_name=settings.app_name,
        project_goal=(
            "Detect marine oil spills using AI-powered satellite "
            "image analysis and provide rapid environmental "
            "response support."
        ),
        project_objectives=[
            "Detect oil spills using a trained U-Net segmentation model",
            "Estimate spill extent and affected area",
            "Predict spill drift using weather conditions",
            "Assess environmental and economic impact",
            "Identify the most probable AIS vessel responsible",
            "Recommend cleanup strategies",
            "Automatically generate incident reports",
        ],
        spill_location=(
            f"{incident.get('latitude')}, {incident.get('longitude')}"
        ),
        detection_time=incident.get("detected_at", "Unknown"),
        spill_detected=True,
        confidence=incident.get("confidence", 0),
        spill_area=incident.get("spill_area_km2", 0),
        risk_score=incident.get("risk_score", 0),
        risk_level=incident.get("risk_level", "UNKNOWN"),
        weather={
            "Wind Speed": f"{weather.get('wind_speed', 'N/A')} km/h",
            "Wind Direction": (
                f"{weather.get('wind_direction', 'N/A')} deg"
            ),
            "Current Speed": (
                f"{incident.get('current_speed', 'N/A')} m/s"
            ),
            "Current Direction": (
                f"{incident.get('current_direction', 'N/A')} deg"
            ),
        },
        drift_prediction=_drift_summary(incident.get("drift", [])),
        environmental_summary={
            "Nearest Coast": (
                f"{env_report['Nearest Coastline']['distance']} km"
                if "Nearest Coastline" in env_report
                else "N/A"
            ),
            "Protected Marine Area": (
                f"{env_report['Nearest Protected Area']['distance']} km"
                if "Nearest Protected Area" in env_report
                else "N/A"
            ),
            "Fishing Zone": (
                f"{env_report['Nearest Fishing Zone']['distance']} km"
                if "Nearest Fishing Zone" in env_report
                else "N/A"
            ),
        },
        suspected_vessel=incident.get("suspect_vessel", {}),
        economic_summary={
            "Cleanup Cost": (
                f"${eco_report['Cleanup Cost ($)']}"
                if "Cleanup Cost ($)" in eco_report
                else "N/A"
            ),
            "Economic Loss": (
                f"${eco_report['Total Economic Loss ($)']}"
                if "Total Economic Loss ($)" in eco_report
                else "N/A"
            ),
        },
        recommendations=(
            incident.get("cleanup", {}).get("Recommendations", [])
            or []
        ),
    )


@router.get("/latest")
def download_latest_report():

    if not REPORT_PATH.exists():

        raise HTTPException(
            status_code=404,
            detail="No report has been generated yet.",
        )

    return FileResponse(
        REPORT_PATH,
        filename="OceanSpill_AI_Incident_Report.pdf",
        media_type="application/pdf",
    )


@router.get("/generate")
def generate_report():

    incident = latest_incident()

    if incident is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "No incident to report yet. Start live monitoring "
                "or upload an image to /detection/predict first."
            ),
        )

    report_path = incident.get("report_path")

    if report_path and Path(report_path).exists():

        return FileResponse(
            report_path,
            filename=Path(report_path).name,
            media_type="application/pdf",
        )

    # Regenerate from the incident data
    report = _report_from_incident(incident)

    output_file = ReportGenerator().generate(report)

    return FileResponse(
        output_file,
        filename="OceanSpill_AI_Incident_Report.pdf",
        media_type="application/pdf",
    )
