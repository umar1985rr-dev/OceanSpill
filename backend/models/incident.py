"""
Incident model for oil spill detection records.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Incident(Base):
    """
    Oil spill incident record.

    Stores all detection data, impact analysis, and response information
    for each detected oil spill event.
    """
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(100), unique=True, index=True, nullable=False)  # INC-YYYYMMDD-HHMMSS-F###

    # Detection data
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    spill_percentage = Column(Float, default=0.0)
    spill_area_km2 = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(50), default="LOW")

    # Frame data
    frame_id = Column(String(100), nullable=True)
    image_path = Column(String(500), nullable=True)
    source = Column(String(50), default="sentinel_hub")  # e.g. sentinel_hub

    # Weather data
    wind_speed = Column(Float, default=0.0)
    wind_direction = Column(Float, default=0.0)
    current_speed = Column(Float, default=0.0)
    current_direction = Column(Float, default=0.0)

    # Analysis results (JSON)
    impact_data = Column(JSON, nullable=True)
    drift_data = Column(JSON, nullable=True)
    cleanup_data = Column(JSON, nullable=True)
    suspect_vessel = Column(JSON, nullable=True)

    # Status
    status = Column(String(50), default="detected")  # detected, investigating, resolved, false_positive
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Report
    report_path = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key to user who acknowledged/resolved
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"<Incident(id={self.id}, incident_id='{self.incident_id}', risk_level='{self.risk_level}')>"

    def to_dict(self):
        """Convert incident to dictionary."""
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "spill_percentage": self.spill_percentage,
            "spill_area_km2": self.spill_area_km2,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "frame_id": self.frame_id,
            "image_path": self.image_path,
            "source": self.source,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "current_speed": self.current_speed,
            "current_direction": self.current_direction,
            "impact": self.impact_data,
            "drift": self.drift_data,
            "cleanup": self.cleanup_data,
            "suspect_vessel": self.suspect_vessel,
            "status": self.status,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes,
            "report_path": self.report_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
