"""
Incidents API: CRUD for oil spill incidents.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from backend.database import get_db
from backend.models.incident import Incident
from backend.core.security import get_current_user, require_roles
from backend.models.user import User

router = APIRouter(prefix="/incidents", tags=["Incidents"])


# ── Schemas ─────────────────────────────────────────────────


class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    detected_at: str
    latitude: float
    longitude: float
    spill_percentage: float
    spill_area_km2: float
    confidence: float
    risk_score: int
    risk_level: str
    frame_id: int
    image_path: str
    source: str
    wind_speed: Optional[float]
    wind_direction: Optional[float]
    current_speed: Optional[float]
    current_direction: Optional[float]
    impact_data: dict
    drift_data: List[dict]
    cleanup_data: dict
    suspect_vessel: dict
    status: str
    resolved_at: Optional[str]
    resolution_notes: Optional[str]
    report_path: Optional[str]
    acknowledged_by: Optional[int]

    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    incidents: List[IncidentResponse]
    total: int
    page: int
    page_size: int


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    resolution_notes: Optional[str] = None


# ── Endpoints ───────────────────────────────────────────────


def _incident_to_response(incident: Incident) -> IncidentResponse:
    return IncidentResponse(
        id=incident.id,
        incident_id=incident.incident_id,
        detected_at=incident.detected_at.isoformat() if incident.detected_at else None,
        latitude=incident.latitude,
        longitude=incident.longitude,
        spill_percentage=incident.spill_percentage,
        spill_area_km2=incident.spill_area_km2,
        confidence=incident.confidence,
        risk_score=incident.risk_score,
        risk_level=incident.risk_level,
        frame_id=incident.frame_id,
        image_path=incident.image_path,
        source=incident.source,
        wind_speed=incident.wind_speed,
        wind_direction=incident.wind_direction,
        current_speed=incident.current_speed,
        current_direction=incident.current_direction,
        impact_data=incident.impact_data or {},
        drift_data=incident.drift_data or [],
        cleanup_data=incident.cleanup_data or {},
        suspect_vessel=incident.suspect_vessel or {},
        status=incident.status,
        resolved_at=incident.resolved_at.isoformat() if incident.resolved_at else None,
        resolution_notes=incident.resolution_notes,
        report_path=incident.report_path,
        acknowledged_by=incident.acknowledged_by,
    )


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(open|acknowledged|resolved)$"),
    risk_level: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all incidents with pagination and filtering."""
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)
    if risk_level:
        query = query.filter(Incident.risk_level == risk_level)
    if start_date:
        try:
            dt = datetime.fromisoformat(start_date)
            query = query.filter(Incident.detected_at >= dt)
        except ValueError:
            pass
    if end_date:
        try:
            dt = datetime.fromisoformat(end_date)
            query = query.filter(Incident.detected_at <= dt)
        except ValueError:
            pass

    total = query.count()
    incidents = (
        query.order_by(Incident.detected_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return IncidentListResponse(
        incidents=[_incident_to_response(i) for i in incidents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific incident by ID."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )
    return _incident_to_response(incident)


@router.get("/by-id/{incident_id_str}", response_model=IncidentResponse)
def get_incident_by_string_id(
    incident_id_str: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific incident by incident_id string (e.g., INC-20260814-123456-F1)."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id_str).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )
    return _incident_to_response(incident)


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    current_user: User = Depends(require_roles(["admin", "operator"])),
    db: Session = Depends(get_db),
):
    """Update incident status and resolution notes (admin/operator only)."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    if payload.status is not None:
        incident.status = payload.status
        if payload.status == "resolved":
            incident.resolved_at = datetime.utcnow()
            incident.acknowledged_by = current_user.id

    if payload.resolution_notes is not None:
        incident.resolution_notes = payload.resolution_notes

    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)

    return _incident_to_response(incident)


@router.get("/stats/summary")
def incident_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get incident statistics summary."""
    from sqlalchemy import func

    total = db.query(Incident).count()
    open_count = db.query(Incident).filter(Incident.status == "open").count()
    acknowledged_count = db.query(Incident).filter(Incident.status == "acknowledged").count()
    resolved_count = db.query(Incident).filter(Incident.status == "resolved").count()

    risk_levels = db.query(
        Incident.risk_level, func.count(Incident.id)
    ).group_by(Incident.risk_level).all()

    return {
        "total": total,
        "open": open_count,
        "acknowledged": acknowledged_count,
        "resolved": resolved_count,
        "by_risk_level": {level: count for level, count in risk_levels},
    }